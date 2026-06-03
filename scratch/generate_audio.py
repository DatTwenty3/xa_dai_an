import asyncio
import os
import json
import edge_tts
import sys

# Reconfigure stdout to use utf-8 to avoid console encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

VOICE = "vi-VN-HoaiMyNeural"
TTS_RATE = "+15%"

# Hamlet narrations mapping to codes
NARRATIONS = {
    "intro": {
        "text": "Chào mừng quý vị đại biểu đến với Bản đồ số tương tác xã Đại An, tỉnh Trà Vinh. Đây là sản phẩm công nghệ số do CÔNG TY ÂU LẠC thực hiện vào tháng 6 năm 2026. Hệ thống dữ liệu này sẽ được cập nhật liên tục nhằm nâng cao hiệu quả cho công tác quản lý hành chính tại địa phương. Xin trân trọng cảm ơn.",
        "path": "audio/intro.mp3"
    },
    "3006001": {
        "text": "Chào mừng bạn đến với Ấp Chợ, xã Đại An, huyện Trà Cú, tỉnh Trà Vinh. Ấp Chợ mới dự kiến được sáp nhập từ ấp Chợ, ấp Mé Rạch E và một phần ấp Giồng Đình. Sau khi ổn định sáp nhập, ấp Chợ mới có tổng diện tích tự nhiên là 144,5 héc-ta, quy mô dân số đạt 3.136 người với 705 hộ dân.",
        "path": "audio/3006001.mp3"
    },
    "3006002": {
        "text": "Chào mừng bạn đến với Ấp Trà Kha, xã Đại An, huyện Trà Cú, tỉnh Trà Vinh. Ấp Trà Kha mới dự kiến được sáp nhập từ ấp Cây Da và ấp Trà Kha. Sau khi ổn định sáp nhập, ấp Trà Kha mới có tổng diện tích tự nhiên là 328,53 héc-ta, quy mô dân số đạt 3.087 người với 704 hộ dân.",
        "path": "audio/3006002.mp3"
    },
    "3006003": {
        "text": "Chào mừng bạn đến với Ấp Giồng Đình, xã Đại An, huyện Trà Cú, tỉnh Trà Vinh. Ấp Giồng Đình mới dự kiến được sáp nhập từ ấp Giồng Đình và ấp Xà Lôn. Sau khi ổn định sáp nhập, ấp Giồng Đình mới có tổng diện tích tự nhiên là 372,35 héc-ta, quy mô dân số đạt 3.197 người với 725 hộ dân.",
        "path": "audio/3006003.mp3"
    },
    "3006004": {
        "text": "Chào mừng bạn đến với Ấp Giồng Giữa, xã Đại An, huyện Trà Cú, tỉnh Trà Vinh. Ấp Giồng Giữa mới dự kiến được sáp nhập từ ấp Mé Rạch B, ấp Giồng Giữa và một phần của ấp Bến Tranh và Vàm Bến Tranh. Sau khi ổn định sáp nhập, ấp Giồng Giữa mới có tổng diện tích tự nhiên là 902,74 héc-ta, quy mô dân số đạt 2.716 người với 705 hộ dân.",
        "path": "audio/3006004.mp3"
    },
    "3006005": {
        "text": "Chào mừng bạn đến với Ấp Mé Láng, xã Đại An, huyện Trà Cú, tỉnh Trà Vinh. Ấp Mé Láng mới dự kiến được sáp nhập từ ấp Mé Láng, ấp Làng Cá và ấp Bến Chùa. Sau khi ổn định sáp nhập, ấp Mé Láng mới có tổng diện tích tự nhiên là 359,47 héc-ta, quy mô dân số đạt 3.525 người với 816 hộ dân.",
        "path": "audio/3006005.mp3"
    },
    "3006006": {
        "text": "Chào mừng bạn đến với Ấp Định An, xã Đại An, huyện Trà Cú, tỉnh Trà Vinh. Ấp Định An mới dự kiến được sáp nhập từ ấp Định An, ấp Cá Lóc, ấp Bến Tranh và ấp Vàm Bến Tranh. Sau khi ổn định sáp nhập, ấp Định An mới có tổng diện tích tự nhiên là 751,92 héc-ta, quy mô dân số đạt 3.611 người với 745 hộ dân.",
        "path": "audio/3006006.mp3"
    },
    "3006007": {
        "text": "Chào mừng bạn đến với Ấp Giồng Lớn, xã Đại An, huyện Trà Cú, tỉnh Trà Vinh. Ấp Giồng Lớn mới dự kiến được sáp nhập từ ấp Giồng Lớn A và ấp Giồng Lớn B. Sau khi ổn định sáp nhập, ấp Giồng Lớn mới có tổng diện tích tự nhiên là 552,19 héc-ta, quy mô dân số đạt 3.764 người với 861 hộ dân.",
        "path": "audio/3006007.mp3"
    }
}

async def generate_file(key, info):
    text = info["text"]
    path = info["path"]
    print(f"Generating TTS for {key} -> {path}...")
    
    for attempt in range(1, 6):
        try:
            communicate = edge_tts.Communicate(text, VOICE, rate=TTS_RATE)
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
    print("=== STARTING NARRATION TTS GENERATION ===")
    
    tasks = []
    for key, info in NARRATIONS.items():
        tasks.append(generate_file(key, info))
        
    results = await asyncio.gather(*tasks)
    success_count = sum(1 for r in results if r)
    print(f"\n=== TTS GENERATION COMPLETED: {success_count}/{len(NARRATIONS)} succeeded ===")

if __name__ == "__main__":
    asyncio.run(main())
