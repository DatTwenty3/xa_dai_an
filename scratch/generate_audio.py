import asyncio
import os
import json
import edge_tts
import sys
import unicodedata
import re

# Reconfigure stdout to use utf-8 to avoid console encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def normalize_name(name):
    """Normalize names to match across text file and json config."""
    name = unicodedata.normalize('NFC', name).lower().strip()
    # Remove common prefixes
    if name.startswith("ấp "):
        name = name[3:].strip()
    elif name.startswith("ấp "):
        name = name[4:].strip()
    return name

def clean_tts_text(text):
    """Format and clean the text for optimal TTS pronunciation."""
    # Normalize Unicode characters to NFC (precomposed) to prevent TTS spelling out words like "Ấp"
    text = unicodedata.normalize('NFC', text)
    
    # Convert 'ha' abbreviation to full word 'héc-ta'
    text = re.sub(r'\bha\b', 'héc-ta', text)
    
    # Replace parentheses with natural phrasing
    # Example: (64 hộ) -> , với 64 hộ,
    text = re.sub(r'\(([^)]+)\)', r', với \1,', text)
    
    # Clean up double punctuations and spaces
    text = text.replace(",.", ".").replace(", .", ".").replace("..", ".").replace(" ,", ",").replace("  ", " ")
    return text.strip()

async def generate_file(key, text, voice, rate, path):
    print(f"Generating TTS for {key} -> {path}...")
    print(f"  Text: \"{text}\"")
    
    for attempt in range(1, 6):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            await communicate.save(path)
            if os.path.exists(path) and os.path.getsize(path) > 1000:
                print(f"  [SUCCESS] Saved {path} ({os.path.getsize(path)} bytes)")
                return True
        except Exception as e:
            print(f"  [ATTEMPT {attempt} FAILED] {e}")
            await asyncio.sleep(2 * attempt)
    print(f"  [ERROR] All attempts failed for {key}")
    return False

async def main():
    os.makedirs("audio", exist_ok=True)
    print("=== STARTING DYNAMIC NARRATION TTS GENERATION ===")
    
    # 1. Load commune config
    config_path = "commune-config.json"
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found!")
        sys.exit(1)
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    commune_name = config.get("commune_name", "Đại An")
    province_name = config.get("province_name", "Trà Vinh")
    year = config.get("year", "2026")
    month = config.get("month", "6")
    company_name = config.get("company_name", "CÔNG TY ÂU LẠC")
    voice = config.get("voice", "vi-VN-HoaiMyNeural")
    tts_rate = config.get("tts_rate", "+15%")
    
    # 2. Load compiled config for hamlet code mappings
    compiled_config_path = "map data/compiled-config.json"
    if not os.path.exists(compiled_config_path):
        print(f"Error: {compiled_config_path} not found! Please run sync_data.py first.")
        sys.exit(1)
        
    with open(compiled_config_path, "r", encoding="utf-8") as f:
        compiled_config = json.load(f)
        
    hamlets = compiled_config.get("hamlets", [])
    name_to_code = {}
    for h in hamlets:
        h_name = h.get("name", "")
        h_code = h.get("ma", "")
        if h_name and h_code:
            name_to_code[normalize_name(h_name)] = h_code
            
    print(f"Loaded {len(name_to_code)} hamlet mappings from config.")
    
    # 3. Read and parse thong_tin_sap_nhap.txt
    txt_path = "thong_tin_sap_nhap.txt"
    if not os.path.exists(txt_path):
        print(f"Error: {txt_path} not found!")
        sys.exit(1)
        
    hamlet_texts = {}
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            parts = line.split(":", 1)
            raw_name = parts[0].strip()
            raw_detail = parts[1].strip()
            
            normalized = normalize_name(raw_name)
            code = name_to_code.get(normalized)
            if code:
                if raw_detail:
                    raw_detail = raw_detail[0].upper() + raw_detail[1:]
                
                # Exclude welcome greeting, use name and detail directly, NFC normalized
                full_text = f"{raw_name}. {raw_detail}"
                cleaned_text = clean_tts_text(full_text)
                
                hamlet_texts[code] = {
                    "name": raw_name,
                    "text": cleaned_text,
                    "path": f"audio/{code}.mp3"
                }
            else:
                print(f"Warning: Could not match hamlet name '{raw_name}' (normalized: '{normalized}') to any code.")
                
    # 4. Add intro narration
    intro_text = f"Chào mừng quý vị đại biểu đến với Bản đồ số tương tác xã {commune_name}, tỉnh {province_name}. Đây là sản phẩm công nghệ số do {company_name} thực hiện vào tháng {month} năm {year}. Hệ thống dữ liệu này sẽ được cập nhật liên tục nhằm nâng cao hiệu quả cho công tác quản lý hành chính tại địa phương. Xin trân trọng cảm ơn."
    hamlet_texts["intro"] = {
        "name": "Giới thiệu chung",
        "text": clean_tts_text(intro_text),
        "path": "audio/intro.mp3"
    }
    
    # 5. Generate audio files
    tasks = []
    for key, info in hamlet_texts.items():
        tasks.append(generate_file(key, info["text"], voice, tts_rate, info["path"]))
        
    results = await asyncio.gather(*tasks)
    success_count = sum(1 for r in results if r)
    print(f"\n=== TTS GENERATION COMPLETED: {success_count}/{len(hamlet_texts)} succeeded ===")

if __name__ == "__main__":
    asyncio.run(main())
