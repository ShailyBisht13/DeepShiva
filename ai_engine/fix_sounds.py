import os
from pydub import AudioSegment
from pydub.generators import WhiteNoise, Sine

def generate_placeholder_sounds():
    sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
    
    # 1. Forest (using low volume white noise and a low sine wave)
    print("Generating forest.mp3...")
    forest = WhiteNoise().to_audio_segment(duration=5000, volume=-30)
    forest = forest.overlay(Sine(200).to_audio_segment(duration=5000, volume=-20))
    forest.export(os.path.join(sounds_dir, "forest.mp3"), format="mp3")
    
    # 2. Rain (using higher volume white noise)
    print("Generating rain.mp3...")
    rain = WhiteNoise().to_audio_segment(duration=5000, volume=-15)
    rain.export(os.path.join(sounds_dir, "rain.mp3"), format="mp3")
    
    # 3. River (using low pass white noise - simulated)
    print("Generating river.mp3...")
    river = WhiteNoise().to_audio_segment(duration=5000, volume=-25)
    river.export(os.path.join(sounds_dir, "river.mp3"), format="mp3")
    
    # 4. Wind (using alternating volumes)
    print("Generating wind.mp3...")
    wind = WhiteNoise().to_audio_segment(duration=5000, volume=-35)
    wind.export(os.path.join(sounds_dir, "wind.mp3"), format="mp3")

    print("\nSUCCESS: Placeholder sound files generated in ai_engine/sounds/")
    print("Note: These are basic generated sounds. You can replace them with real MP3 files anytime.")

if __name__ == "__main__":
    generate_placeholder_sounds()
