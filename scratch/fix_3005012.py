import asyncio
import edge_tts
import os

async def main():
    text = "Chào mừng bạn đến với Ấp Ô Rồm. Đây là đơn vị hành chính thuộc huyện Cầu Kè, tỉnh Trà Vinh. Về diện tích, Ấp Ô Rồm có diện tích tự nhiên là 334768 héc-ta. Quy mô dân số của Ấp đạt khoảng 1848 người. Mật độ dân số trung bình đạt 55,2 người trên một héc-ta."
    output_path = "audio/3005012.mp3"
    voice = "vi-VN-HoaiMyNeural"
    
    print(f"Generating TTS for {output_path}...")
    for attempt in range(1, 6):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"Success! Saved audio to {output_path} ({os.path.getsize(output_path)} bytes)")
                return
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            await asyncio.sleep(2 * attempt)
    print("All attempts failed.")

if __name__ == "__main__":
    asyncio.run(main())
