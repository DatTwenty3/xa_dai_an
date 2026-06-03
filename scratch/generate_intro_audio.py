import asyncio
import os
import edge_tts

VOICE = "vi-VN-HoaiMyNeural"
TTS_RATE = "+15%"
TEXT = "Chào mừng quý vị đại biểu đến với Bản đồ số tương tác xã Cầu Kè, tỉnh Vĩnh Long. Đây là sản phẩm công nghệ số do CÔNG TY ÂU LẠC thực hiện vào tháng 5 năm 2026. Hệ thống dữ liệu này sẽ được cập nhật liên tục nhằm nâng cao hiệu quả cho công tác quản lý hành chính tại địa phương. Xin trân trọng cảm ơn."
OUTPUT_PATH = "audio/intro.mp3"

async def generate():
    os.makedirs("audio", exist_ok=True)
    print(f"Generating intro audio using edge-tts...")
    await edge_tts.Communicate(TEXT, VOICE, rate=TTS_RATE).save(OUTPUT_PATH)
    if os.path.exists(OUTPUT_PATH) and os.path.getsize(OUTPUT_PATH) > 0:
        print(f"Success! Generated {OUTPUT_PATH} ({os.path.getsize(OUTPUT_PATH)} bytes)")
    else:
        print("Failed to generate audio file.")

if __name__ == "__main__":
    asyncio.run(generate())
