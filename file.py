import pygame
import speech_recognition as sr
from nltk import *
from nltk.stem import WordNetLemmatizer
from moviepy.editor import *
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Speech-O-Sign")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (100, 149, 237)

# Fonts
FONT = pygame.font.Font(None, 36)

# Button dimensions
BUTTON_WIDTH, BUTTON_HEIGHT = 150, 50

# Create buttons
record_button = pygame.Rect(225, 150, BUTTON_WIDTH, BUTTON_HEIGHT)
generate_button = pygame.Rect(225, 250, BUTTON_WIDTH, BUTTON_HEIGHT)

# Placeholder for recognized text
recognized_text = ""
display_text = "Click 'Record' to start speaking"
display_text2 = display_text

# Function to record audio and convert to text
def record_audio():
    global recognized_text, display_text
    r = sr.Recognizer()
    with sr.Microphone() as source:
        display_text = "Listening..."
        pygame.display.update()  # Update the display immediately
        print('Listening...')
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        recognized_text = r.recognize_google(audio).lower()
        display_text = f"Recognized"
        display_text2 = f"Recognized: {recognized_text}"
        print(f"Recognized text: {display_text2}")
    except sr.UnknownValueError:
        recognized_text = ""
        display_text = "Could not understand the audio."
        print("Could not understand the audio.")
    except sr.RequestError:
        recognized_text = ""
        display_text = "API error occurred."
        print("API error occurred.")

# Function to process text and generate sign language videos
def generate_sign_language():
    global display_text
    if not recognized_text:
        display_text = "No recognized text to process."
        print("No recognized text to process.")
        return

    # PHASE 2: Process text (as per your earlier code)
    tokenized_text = word_tokenize(recognized_text)
    tags = pos_tag(tokenized_text)
    text = ""
    l = WordNetLemmatizer()

    for w, t in tags:
        if t == 'VBG':
            x = l.lemmatize(w, 'v')
            x += " "
            text += x

        if t != 'VBZ' and t != 'DT' and t != 'VBP':
            w += ' '
            text += w

    display_text = f"Processed Text: {text}"
    print(f"Processed ISL-compatible text: {text}")
    word_list = text.split()

    # PHASE 4: Map to sign language videos
    clips = []
    sign_directory = r'Signs'  # Adjust to your folder

    for word in word_list:
        word_clip_found = False
        word_video = os.path.join(sign_directory, f'{word}.mp4')

        if os.path.exists(word_video):
            clip = VideoFileClip(word_video).resize(1)
            clip = clip.fx(vfx.speedx, 2.75)
            clips.append(clip)
            word_clip_found = True
        else:
            char_clips = []
            for char in word:
                char_image = os.path.join(sign_directory, f'{char}.jpg')
                if os.path.exists(char_image):
                    clip = ImageClip(char_image, duration=0.5).resize(0.25)
                    char_clips.append(clip)

            if char_clips:
                word_clip = concatenate_videoclips(char_clips, method="compose")
                clips.append(word_clip)
                word_clip_found = True

        if not word_clip_found:
            print(f"No video or images found for word: {word}")

    if clips:
        try:
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile("output.mp4")
            display_text = "Generated video for ISL."
            print("Video generated successfully!")
            op = VideoFileClip("output.mp4")
            op.preview()
        except Exception as e:
            display_text = f"Error generating video: {e}"
            print(f"Error: {e}")
    else:
        display_text = "No clips to generate video."
        print("No clips to generate video.")

# Main loop
running = True
while running:
    screen.fill(WHITE)

    # Draw the buttons
    pygame.draw.rect(screen, BLUE, record_button)
    pygame.draw.rect(screen, BLUE, generate_button)

    # Draw the button text
    screen.blit(FONT.render("Record", True, WHITE), (record_button.x + 35, record_button.y + 10))
    screen.blit(FONT.render("Generate", True, WHITE), (generate_button.x + 25, generate_button.y + 10))

    # Display recognized text or status message
    text_surface = FONT.render(display_text, True, BLACK)
    screen.blit(text_surface, (50, 50))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if record_button.collidepoint(event.pos):
                record_audio()
            elif generate_button.collidepoint(event.pos):
                generate_sign_language()
    
    pygame.display.flip()

pygame.quit()