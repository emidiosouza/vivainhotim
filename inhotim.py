import streamlit as st
import openai
import uuid
import time
from openai import OpenAI
import hmac


#Inicialização OpenAI
client = OpenAI()

# Select the preferred model
MODEL = "gpt-4-1106-preview"

# Inicialização da variável audio
audio = None
audio_on = False

# Função para gerar áudio
def generate_audio_from_text(tts_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=tts_text
    )
    # Salvar o arquivo de áudio
    audio_file_path = "audio_output.mp3"
    with open(audio_file_path, "wb") as file:
        file.write(response.content)
    return audio_file_path


st.set_page_config(page_title="Viva INHOTIM", page_icon="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAM1BMVEUAzJsvioEcpIv///9m4MOZ69eM6NI92LOx7+Gt79+48eNU3bzC8+ej7dsp1KsY0aVF2raVZJieAAAAS0lEQVQ4jWNgBAImBqyACSTHMOQUcLOBATtOBewsPMzMvCx8eKxgZWZmweuGUQUjSAEfOwczMxs7P04FLJwcXFwcnAJ4rEABQ0cBAPVEA2w9Ksp7AAAAAElFTkSuQmCC")

# CSS para mudar a fonte dos elementos Markdown para Dosis
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300&family=Noto+Serif:wght@600&display=swap');


html, body, p, textarea {
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
}
            
h1, h2, h3, h4, h5, h6  {
    font-family: 'Noto Serif', serif;
}
        
</style>
""", unsafe_allow_html=True)

#Esconder botão de expansão da imagem
hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''
# Inject custom CSS to set the width of the sidebar
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 300px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(hide_img_fs, unsafe_allow_html=True)

def check_password():
    """Returns `True` if the user had a correct password."""
    
    
    def login_form():

    
        st.image('inhotim-logo.png', width=120)
        st.subheader(":white[Olá! Explore e descubra o Inhotim!]")
        st.write(":white[Sou um assistente criado para te auxiliar a planejar a sua visita e conheçer mais as obras do Inhotim. Antes de começar, insira seus dados de visitante:]")
        
        with st.form("Credentials"):
            st.subheader("")
            st.text_input("Nome de Usuário", key="username", help="Para acessar a demo, peça suas credenciais ao Emídio.")
            st.text_input("Qual a sua senha?", type="password", key="password")
            st.form_submit_button("Viva o Inhotim!", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 Usuário desconhecido ou senha incorreta.")
    return False


if not check_password():
    st.stop()

#Controle de estados
if "session_id" not in st.session_state: # Used to identify each session
    st.session_state.session_id = str(uuid.uuid4())

if "run" not in st.session_state: # Stores the run state of the assistant
    st.session_state.run = {"status": None}

if "messages" not in st.session_state: # Stores the messages of the assistant
    st.session_state.messages = []

if "retry_error" not in st.session_state: # Used for error handling
    st.session_state.retry_error = 0

# Inicializar last_processed_message_id
if "last_processed_message_id" not in st.session_state:
    st.session_state.last_processed_message_id = None



#Configuração da sidebar Streamlit
with st.sidebar: 
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.image('inhotim-logo-branca.png', width=150)
st.sidebar.header("Esse é o Viva Inhotim", divider='green')
with st.sidebar: 	
    st.write("Sou um assistente de visitação do Inhotim, pronto pra te responder sobre nossas obras e instalações.")
    st.write("Posso te ajudar a planejar uma visita especialmente planejada para você.")
    st.write("Conheço muita coisa sobre o Inhotim, então é só me enviar a pergunta ao lado que irei te responder.")
    st.link_button("COMPRE SEU INGRESSO", "https://bileto.sympla.com.br/event/89314/d/229088/s/1552683")
    audio_on = st.toggle('ÁUDIO', help="Aqui você pode ligar e desligar a voz da assistente")
st.sidebar.header("", divider='green')
st.sidebar.markdown("""
    <style>
    .small-font {
        font-size: 10px; /* Ajuste o tamanho da fonte conforme necessário */
    }
    </style>
    <p class="small-font">Desenvolvido pela área de inovação da Kukac para demonstração. Versão atual: 0.0.1</p>
""", unsafe_allow_html=True)

st.subheader("Como você quer viver o Inhotim?", help="""
  # Deixe eu te dar alguns exemplos de questões em que eu posso ajudar:
  - Crie um roteiro para um artista plástico que deseja se inspirar, interessado no uso de madeira na arte.
  - Minha mãe não gosta muito de arte-performance nem de instalações muito intensas. Crie um roteiro de vistação pra gente.
  - Inclua no meu roteiro uma parada para almoço em um restaurante não muito caro.
""", divider='green')

#Configurações OpenAI
if "assistant" not in st.session_state:
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    # Load the previously created assistant
    st.session_state.assistant = openai.beta.assistants.retrieve(st.secrets["OPENAI_ASSISTANT"])

    # Create a new thread for this session
    st.session_state.thread = client.beta.threads.create(
        metadata={
            'session_id': st.session_state.session_id,
        }
    )

# Se a run anterior completar, ele carrega as mensagens.
elif hasattr(st.session_state.run, 'status') and st.session_state.run.status == "completed":
    # Retrieve the list of messages
    st.session_state.messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread.id
    )

# Mostrar fontes
    for thread_message in st.session_state.messages:
        for message_content in thread_message.content:
            # Access the actual text content
            message_content = message_content.text
            annotations = message_content.annotations
            citations = []
            
            # Iterate over the annotations and add footnotes
            for index, annotation in enumerate(annotations):
                # Replace the text with a footnote
                message_content.value = message_content.value.replace(annotation.text, f' [{index}]')
            
                # Gather citations based on annotation attributes
                if (file_citation := getattr(annotation, 'file_citation', None)):
                    cited_file = client.files.retrieve(file_citation.file_id)
                    citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
                elif (file_path := getattr(annotation, 'file_path', None)):
                    cited_file = client.files.retrieve(file_path.file_id)
                    citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
                    # Note: File download functionality not implemented above for brevity

            # Add footnotes to the end of the message before displaying to user
            message_content.value += '\n' + '\n'.join(citations)

 # Iterando nas mensagens para encontrar a última mensagem do bot
    if st.session_state.messages.data:
        for message in st.session_state.messages.data:
            if message.role == "assistant":
                ultima_mensagem = message
                break
            
        if ultima_mensagem and ultima_mensagem.content: # Verificando se a última mensagem do assistente foi encontrada
            if audio_on:
                audio_file_path = generate_audio_from_text(ultima_mensagem.content[0].text.value)          


# Mostrar mensagens na ordem reversa
    for message in reversed(st.session_state.messages.data):
        if message.role in ["user", "assistant"]:
            with st.chat_message(message.role):
                for content_part in message.content:
                    message_text = content_part.text.value
                    st.markdown(message_text)



# Pega input do usuário
if prompt := st.chat_input("Escreva aqui a sua mensagem."):
    with st.chat_message('user'):
        st.write(prompt)

    # Manda input para a thread
    st.session_state.messages = client.beta.threads.messages.create(
        thread_id=st.session_state.thread.id,
        role="user",
        content=prompt
    )

# Processa a thread
    st.session_state.run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread.id,
        assistant_id=st.session_state.assistant.id,
    )
    if st.session_state.retry_error < 3:
        time.sleep(1) # Wait 1 second before checking run status
        st.rerun()

# ERROR HANDLING
# Check if 'run' object has 'status' attribute
if hasattr(st.session_state.run, 'status'):
    # Handle the 'running' status
    if st.session_state.run.status == "running":
        with st.chat_message('assistant'):
            st.write("Thinking ......")
        if st.session_state.retry_error < 3:
            time.sleep(1)  # Short delay to prevent immediate rerun, adjust as needed
            st.rerun()

    # Handle the 'failed' status
    elif st.session_state.run.status == "failed":
        st.session_state.retry_error += 1
        with st.chat_message('assistant'):
            if st.session_state.retry_error < 3:
                st.write("Run failed, retrying ......")
                time.sleep(3)  # Longer delay before retrying
                st.rerun()
            else:
                st.error("FAILED: The OpenAI API is currently processing too many requests. Please try again later ......")

    # Handle any status that is not 'completed'
    elif st.session_state.run.status != "completed":
        # Attempt to retrieve the run again, possibly redundant if there's no other status but 'running' or 'failed'
        st.session_state.run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id,
            run_id=st.session_state.run.id,
        )
        if st.session_state.retry_error < 3:
            time.sleep(3)
            st.rerun()

    elif st.session_state.run.status == "completed":
        if audio_on:
            st.audio(audio_file_path, format='audio/mp3')
