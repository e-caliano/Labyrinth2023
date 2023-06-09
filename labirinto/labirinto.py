import os
from PIL import Image
import json


class Labirinto:

    """
    La classe Labirinto rappresenta un labirinto e si occupa di leggere e
    manipolare il labirinto a partire da un file JSON o da un'immagine forniti in input.
    """

    def __init__(self, percorso_file):

        """
        Costruttore della classe Labirinto:
        la classe prende in input un percorso di file come argomento, controlla se il file esiste,
        quindi inizializza alcune variabili, come una lista di liste (assimilabile a una matrice) per il labirinto,
        una lista per i punti di partenza, una tupla per il punto di arrivo e un'immagine per il labirinto.
        """

        # assegnazione del percorso del file in input
        self.percorso_file = percorso_file

        # lista di liste (assimilabile a una matrice) che ospiterà il labirinto
        self.maze = []
        # lista che ospiterà i punti di partenza
        self.start = []
        # tupla che ospita il punto di arrivo
        self.end = ()
        # immagine che conterrà l'immagine del labirinto,
        # utile soprattutto se input è un JSON
        self.image = None

    def gestisci_input(self):

        """

        Metodo per il parsing dell'input: se il file è .json allora dovrò chiamare una funzione che
        dal json mi crea una istanza del labirinto,
        se il file è di tipo immagine allora dovrò chiamare un metodo che
        crea un'istanza del labirinto a partire dall'immagine.
        :return:
        """

        # Ottengo il nome del file e la sua estensione
        name, estensione = os.path.splitext(os.path.basename(self.percorso_file))
        # controllo l'estensione ed eseguo l'azione appropriata
        if estensione == '.json':
            # carico il labirinto dal file JSON
            with open(self.percorso_file) as json_file:
                data = json.load(json_file)
            # chiamo la funzione che elabora il JSON per creare il labirinto e manipolarlo
            self.labirinto_from_json(data)
            # salvo l'immagine del labirinto nella cartella json_image
            self.path_image = './json_image/' + name + '.png'
            self.image.save(self.path_image)
        # controllo che l'estensione sia di tipo TIFF, JPEG O PNG
        elif estensione in ['.tiff', '.jpeg', '.png']:
            # carico il labirinto dall'immagine
            self.path_image = self.percorso_file
            self.image = Image.open(self.percorso_file)
            self.labirinto_from_image()
        # in tutti gli altri casi non devo supportare l'estensione
        else:
            # gestione dell'errore se l'estensione non è supportata
            raise ValueError("Estensione del file inesistente o non supportata")


    def labirinto_from_json(self, data):

        """
        Metodo per creare istanza del labirinto a partire dal file json di input
        :return:
        """

        # controllo che il JSON abbia i campi prestabiliti
        if set(list(data.keys())) != {"larghezza", "altezza", "pareti", "iniziali", "finale", "costi"}:
            raise ValueError("Struttura file JSON non supportata")
        # popolo la matrice che ospita il labirinto
        for i in range(data["altezza"]):
            maze_row = []
            for j in range(data["larghezza"]):
                maze_row.append(1)
            self.maze.append(maze_row)

        # Popola la matrice con le pareti
        for wall in data["pareti"]:
            if wall["orientamento"] == "H":
                for i in range(wall["lunghezza"]):
                    self.maze[wall["posizione"][0]][wall["posizione"][1] + i] = 0
            elif wall["orientamento"] == "V":
                for i in range(wall["lunghezza"]):
                    self.maze[wall["posizione"][0] + i][wall["posizione"][1]] = 0

        # Popola con le posizioni iniziali
        for iniziale in data["iniziali"]:
            i = iniziale[0]
            j = iniziale[1]
            self.start.append((i, j))


        # Popola con la posizione di arrivo
        i = data["finale"][0][0]
        j = data["finale"][0][1]
        self.end = (i, j)


        # Popolo con le caselle in scala di grigi
        for costo in data["costi"]:
            i = costo[0]
            j = costo[1]
            peso = costo[2] + 1
            self.maze[i][j] = peso

        self.json_to_image()


    def json_to_image(self):

        """
        Metodo per convertire la matrice del labirinto in un'immagine
        :return:
        """

        # creazione di un'immagine vuota tramite Image,
        # che abbia dimensione pari alla matrice che contiene il labirinto
        self.image = Image.new("RGB", (len(self.maze[0]), len(self.maze)))
        pixels = self.image.load()
        # Impostazione dei pixel dell'immagine in base alla lista di liste del labirinto
        for i in range(len(self.maze)):
            for j in range(len(self.maze[0])):
                if self.maze[i][j] == 0:
                    # imposto il muro inizializzato a 0
                    pixels[j, i] = (0, 0, 0)  # muro = nero
                    # imposto il cammino inizializzato a 1
                elif self.maze[i][j] == 1:
                    pixels[j, i] = (255, 255, 255)  # cammino = bianco
                else:
                    # imposto il cammino pesato
                    # cammino pesato = grigio scuro
                    pixels[j, i] = ((self.maze[i][j] - 1) * 16, (self.maze[i][j] - 1) * 16, (self.maze[i][j] - 1) * 16)
        # imposto l'inizio e la fine del labirinto
        i = self.end[0]
        j = self.end[1]
        pixels[j, i] = (255, 0, 0)  # arrivo = rosso
        for st in self.start:
            i = st[0]
            j = st[1]
            pixels[j, i] = (0, 255, 0)  # partenza = verde


    def labirinto_from_image(self):
        """
        Metodo che consente di estrarre un labirinto rappresentato da un'immagine (in formato PNG, JPEG, etc.)
        e per ottenere una matrice del labirinto.
        :return:
        """
        # apre l'immagine e ottiene i dati dei pixel
        pixel = self.image.load()
        larghezza, altezza = self.image.size

        # inizializzo la matrice del labirinto
        labirinto = []
        for i in range(altezza):
            labirinto.append([0] * larghezza)

        # dizionario di corrispondenza tra valore di grigio e costo
        grigio_costo = {
            16: 1,
            32: 2,
            48: 3,
            64: 4,
            80: 5,
            96: 6,
            112: 7,
            128: 8,
            144: 9,
            160: 10,
            176: 11,
            192: 12,
            208: 13,
            224: 14,
            240: 15
        }

        # analizzo i pixel dell'immagine e costruisco la matrice del labirinto
        for y in range(altezza):
            for x in range(larghezza):
                r, g, b = pixel[x, y]
                # se i pixel sono verdi rappresentano l'inizio, attraversabile =1
                if r == 0 and g == 255 and b == 0:
                    self.start.append((y, x))
                    labirinto[y][x] = 1
                # se il pixel è rosso è la fine, attraversabile = 1
                elif r == 255 and g == 0 and b == 0:
                    self.end = (y, x)
                    labirinto[y][x] = 1
                # pixel nero = muro = 0
                elif r == 0 and g == 0 and b == 0:
                    labirinto[y][x] = 0
                # pixel bianco = posizione attraversabile = 1
                elif r == 255 and g == 255 and b == 255:
                    labirinto[y][x] = 1
                # pixel grigio = casella con costo
                else:
                    # determino il valore del pixel in scala di grigi
                    valore_grigio = int(round(0.2989 * r + 0.5870 * g + 0.1140 * b))
                    # determino il costo associato al valore del pixel
                    if valore_grigio in grigio_costo:
                        costo = grigio_costo[valore_grigio]
                    else:
                        raise ValueError("Valore di grigio non valido")
                    labirinto[y][x] = costo + 1
        self.maze = labirinto