import time
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import mediapipe as mp
import pyaudio
from vosk import Model, KaldiRecognizer
from pynput.mouse import Button
from pynput.mouse import  Controller as mouse_controller
from pynput.keyboard import Controller as keyboard_controller
from threading import Thread, Event
from queue import Queue

#model = Model(r"C:\Users\usuario\Documents\vosk\vosk-model-small-en-us-0.15")
model = Model(r"C:\Users\gusta\Documents\vosk\vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=8192)
stream.start_stream()

mouse = mouse_controller()
keyboard = keyboard_controller()

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

#inicialização de variaveis
# create an event
exec = False # variavel para checar se algum comando de keyword está em execução
ordem = [] # ordem dos clicks
record_check = Event() # Evento para checar se a thread principal deve começar a gravar os clicks (True = gravar; False = nao gravar )
send_check = Event() # Evento para cheacar se a lista de comandos deve ser enviada 
limite_pisc = 0.3 #tempo em segundos para considerr uma piscada como voluntária
pisc_controle_d = False
pisc_controle_e = False
piscs_d = 5*[False] # vetor para armazenar os ultimos 3 estados de piscada do olho direito (para evitar que um erro de detecção seja reforçado)
piscs_e = 5*[False] # vetor para armazenar os ultimos 3 estados de piscada do olho esquerdo (para evitar que um erro de detecção seja reforçado)
inicio_d = fim_d = inicio_e = fim_e = 0
vetor_olho_d = [] # vetor para armazenar a distância entre os pontos do olho direito para gerar threshold de piscadas
vetor_olho_e =[] # vetor para armazenar a distância entre os pontos do olho esquerdo para gerar threshold de piscadas
#iniciaçização de funções

def executar(keywords):
   
   for elemento in keywords:
      coordenadas = elemento[1]
      mouse.position = coordenadas
      if elemento[0]=='d':
         mouse.press(Button.left)
         mouse.release(Button.left) 
         print("click direito em: ", coordenadas)
      else:
         mouse.press(Button.left)
         mouse.release(Button.left) 
         print("click esquerdo em:", coordenadas)

def vosk():
   global exec
   keywords = {}
   comando = False
   while True:
      if (exec == True) and (index < index_max):
         if (time.perf_counter() - inicio) > index:
            mouse.position = keywords[keyw][index][1]
            if keywords[keyw][index][0] == 'd':
               mouse.press(Button.right)
               mouse.release(Button.right)
            else:
               mouse.press(Button.left)
               mouse.release(Button.left)

            
            index = index + 1
         if index == index_max:
            exec = False

      data = stream.read(4096)

      if recognizer.AcceptWaveform(data):
         text = recognizer.Result()
         if text != "":
            if comando == True: 
              keyboard.type(text[14:-3])
              comando = False
            else:
               keyword = text.replace('"','').split()[3]
               if (not comando) and  keyword in keywords:
                  #executar(keywords[keyword])
                  index = 0
                  exec = True
                  keyw = keyword
                  index_max = len(keywords[keyword])
                  inicio = time.perf_counter()
            
               if 'keyboard' in text:
                  comando = True
                
               if(keyword=='start'):
                  #iniciar gravação de novo comando
                  print("gravando")
                  record_check.set()
                
               if ((keyword=='stop') and record_check.is_set()):
                  palavra = text.replace('"','').split()[4]
                  print("finalizado")
                
                  if palavra == '':
                     palavra = 'none'
                  
                  global ordem
                  keywords[palavra] = ordem
                  ordem = []
                  print(keywords)
                  #iniciar gravação de novo comando
                  send_check.set()



def pontos(results):
   #########################################   DISTANCIA ENTRE PONTOS DA BOCA   ##########################################
   db1 = results.multi_face_landmarks[0].landmark[87].y - results.multi_face_landmarks[0].landmark[38].y
   db2 = results.multi_face_landmarks[0].landmark[317].y - results.multi_face_landmarks[0].landmark[268].y
   dbh = results.multi_face_landmarks[0].landmark[306].x - results.multi_face_landmarks[0].landmark[76].x

   db = 100 *(db1 + db2 / 2*dbh)

      ####################################### DISTANCIA ENTRE PONTOS DO OLHO DIREITO ###########################################

   dvd1 = results.multi_face_landmarks[0].landmark[144].y - results.multi_face_landmarks[0].landmark[160].y
   dvd2 = results.multi_face_landmarks[0].landmark[153].y - results.multi_face_landmarks[0].landmark[158].y

   
   
   dhd = results.multi_face_landmarks[0].landmark[133].x - results.multi_face_landmarks[0].landmark[33].x
   dd = 10000 * (dvd1 + dvd2) / 2*dhd

      ####################################### DISTANCIA ENTRE PONTOS DO OLHO ESQUERDO ###########################################
   dve1 = results.multi_face_landmarks[0].landmark[380].y - results.multi_face_landmarks[0].landmark[385].y
   dve2 = results.multi_face_landmarks[0].landmark[373].y - results.multi_face_landmarks[0].landmark[387].y
   
   
   dhe = results.multi_face_landmarks[0].landmark[263].x - results.multi_face_landmarks[0].landmark[362].x



   de = 10000 *(dve1 + dve2) / 2*dhe

   return db, dd, de

thread = Thread(target=vosk)
thread.start()

# For webcam input:
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
cap = cv2.VideoCapture(0)
with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
   while cap.isOpened():
      success, image = cap.read()
      if not success:
         print("Ignoring empty camera frame.")
         # If loading a video, use 'break' instead of 'continue'.
         continue

      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      image.flags.writeable = False
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      
      im_pil = Image.fromarray(image)
      enhancer = ImageEnhance.Contrast(im_pil)
      factor = 1
      im_output = enhancer.enhance(factor)
      im_np = np.asarray(im_output)
      
      results = face_mesh.process(im_np)

      # Draw the face mesh annotations on the image.
      #image.flags.writeable = True
      image = cv2.cvtColor(im_np, cv2.COLOR_RGB2BGR)
      if results.multi_face_landmarks:
        
         if send_check.is_set():
            #print("SALVAR")
            #print(ordem)
            #enviar dados gravados
            send_check.clear()
            record_check.clear()
            #apagando dados gravados
            ordem = []

           
         pos = results.multi_face_landmarks[0].landmark[4]
         angle_control = results.multi_face_landmarks[0].landmark[152].z
         db, dd, de = pontos(results)
         #print(db)
         #print(dd)
         #print(de)
         print(de , "#######################" , dd)

         if db <1:
            #print("boca fechada")
            b = False
            pos_0 = results.multi_face_landmarks[0].landmark[4]
         else:
            b = True
            if 'pos_0' in locals():
               #print("boca aberta")
               if abs(pos.y -pos_0.y) <= 0.06:
                  par_y =  0.5 # parâmetro de deslocamento vertical
               else:
                  par_y = 1
               #print(par_y)

               if abs(pos.x -pos_0.x) <= 0.06:
                  par_x =  0.5 # parâmetro de deslocamento horizontal
               else:
                  par_x = 1

               #print(abs(pos.x -pos_0.x))
               if pos.x > pos_0.x + 0.03:
                  #esquerda
                  mouse.move(-8 * par_x, 0)  
               elif pos.x < pos_0.x - 0.03: 
                  #direita
                  mouse.move(8 * par_x, 0)  
               if pos.y > pos_0.y + 0.02:
                  #baixo")
                  mouse.move(0,8 * par_y) 
               elif pos.y < pos_0.y - 0.02:
                  #cima
                  mouse.move(0,-8 *par_y)   


        


         #if dd<0.025:
         if dd<3 and (not b):
            #FECHADO
            #print("fechado")
            pisc_d = True
         else:
            #ABERTO
            #print("aberto") 
            pisc_d = False

         for i in range(len(piscs_d)-1):
            piscs_d[i] = piscs_d[i+1]
            piscs_d[-1] = pisc_d

         if piscs_d == [False,False,False,True,True]:
            inicio_d = time.perf_counter()
            pisc_controle_d = True
            #print("INICIO")

         if True in piscs_d:
            fim_d = time.perf_counter()
            #print("FIM")
           
         if (fim_d-inicio_d)>limite_pisc and (pisc_controle_d == True) and (dd < de):
            if record_check.is_set():
               ordem.append(('d',mouse.position))
            #print("PISCOU")
            print("click direito")
            mouse.press(Button.right)
            mouse.release(Button.right)
            pisc_controle_d = False
          
         #if de<0.025:
         if de<3 and (not b):
            #FECHADO
            #print("piscou")
            pisc_e = True
         else:
            #ABERTO
            pisc_e = False

         for i in range(len(piscs_e)-1):
            piscs_e[i] = piscs_e[i+1]
            piscs_e[-1] = pisc_e
         
         #print(piscs_e)
         if piscs_e == [False,False,False,True,True]:
            inicio_e = time.perf_counter()
            pisc_controle_e = True
            #print("INICIO")

         if True in piscs_e:
            fim_e = time.perf_counter()
            #print("FIM")
           
         if (fim_e-inicio_e)>limite_pisc and (pisc_controle_e == True) and (de < dd): 
            if record_check.is_set():
               ordem.append(('e',mouse.position))
               #começar a gravar os botoes
               #print("PISCOU")
            print("click esquerdo")
            mouse.press(Button.left)
            mouse.release(Button.left) 
            pisc_controle_e = False
                 
          
      

    # Flip the image horizontally for a selfie-view display.
      cv2.imshow('MediaPipe Face Mesh', cv2.flip(image, 1))
      if cv2.waitKey(5) & 0xFF == 27:
         break
cap.release()