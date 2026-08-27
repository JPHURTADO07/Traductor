import os
import streamlit as st
from bokeh.models.widgets import Button
#from bokeh.io import show
#from bokeh.models import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob



from gtts import gTTS
from googletrans import Translator


st.title("TRADUCTOR.")
st.subheader("Escucho lo que quieres traducir.")


image = Image.open('ciao.jpg')

st.image(image,width=300)
with st.sidebar:
    st.subheader("Traductor.")
    st.write("Presiona el botón, cuando escuches la señal "
                 "habla lo que quieres traducir, luego selecciona"   
                 " la configuración de lenguaje que necesites.")


st.write("Toca el Botón y habla lo que quires traducir")

stt_button = Button(label=" Escuchar  🎤", width=300,  height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;  // Cambia a false
    recognition.interimResults = true;
    recognition.lang = 'es-ES';  // Puedes ajustar el idioma
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    
    recognition.onend = function() {
        console.log("Reconocimiento detenido");
    }
    
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
    try:
        os.mkdir("temp")
    except:
        pass
   st.title("Texto a Audio")
translator = Translator()

text = str(result.get("GET_TEXT"))

# Mapeo de idiomas disponibles (código ISO)
LANGUAGES = {
    "Inglés": "en",
    "Español": "es",
    "Francés": "fr",
    "Alemán": "de",
    "Bengali": "bn",
    "Coreano": "ko",
    "Mandarín": "zh-cn",
    "Japonés": "ja",
}

# Mapeo de acentos/dominios (TLD para gTTS)
ACCENTS = {
    "Defecto": "com",
    "Español": "com.mx",
    "Francés": "fr",
    "Alemán": "de",
    "Reino Unido": "co.uk",
    "Estados Unidos": "com",
    "Canada": "ca",
    "Australia": "com.au",
    "Irlanda": "ie",
    "Sudáfrica": "co.za",
}

# Selectores de idioma
in_lang = st.selectbox("Selecciona el lenguaje de Entrada", list(LANGUAGES.keys()))
input_language = LANGUAGES[in_lang]

out_lang = st.selectbox("Selecciona el lenguaje de salida", list(LANGUAGES.keys()))
output_language = LANGUAGES[out_lang]

# Selector de acento / TLD
english_accent = st.selectbox("Selecciona el acento", list(ACCENTS.keys()))
tld = ACCENTS[english_accent]
    
    
    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text
    
    
    display_output_text = st.checkbox("Mostrar el texto")
    
    if st.button("convertir"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tú audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
    
        if display_output_text:
            st.markdown(f"## Texto de salida:")
            st.write(f" {output_text}")
    
    
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    remove_files(7)
           


        
    



        
    


