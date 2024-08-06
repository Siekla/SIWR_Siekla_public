import numpy as np
import cv2 as cv
import os
from matplotlib import pyplot as plt
from pgmpy.models import FactorGraph
from pgmpy.factors.discrete import DiscreteFactor
from itertools import combinations
from pgmpy.inference import BeliefPropagation
import argparse

# TODO Jakość kodu i raport (2.5/5)
# TODO Raport tylko ogólnie wyjaśnia jak działa model, co oznaczają zmienne losowe oraz czemu służą poszczególne czynniki.
# TODO Kod dobrze okomentowany, ale miejscami mało przejrzysty.

# TODO Skuteczność śledzenia 0.513 (3/5)
# TODO [0.00, 0.0] - 0.0
# TODO (0.0, 0.1) - 0.5
# TODO [0.1, 0.2) - 1.0
# TODO [0.2, 0.3) - 1.5
# TODO [0.3, 0.4) - 2.0
# TODO [0.4, 0.5) - 2.5
# TODO [0.5, 0.6) - 3.0
# TODO [0.6, 0.7) - 3.5
# TODO [0.7, 0.8) - 4.0
# TODO [0.8, 0.9) - 4.5
# TODO [0.9, 1.0) - 5.0

previos_histr = [] # zdeklarownie zmiennej globalnej przechowującej histogramy z wcześniejszego zdjęcia

class write_kord: # klasa służąca do wpisywania koordynatów
    def __init__(self, n_box):
        self.number_of_bboxes = n_box
        if n_box > 0:
            self.bboxes_array = np.zeros((n_box, 4))

    def add_box(self, index, array): # funkcja dodająca boxy
        self.bboxes_array[index] = array


def main():
    # TODO Ta zmienna nie musi być globalna.
    global previos_histr

    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', type=str)
    args = parser.parse_args()

    box = os.path.join(args.data_dir, "bboxes.txt")  # otworzenie oraz czytanie pliku bboxes.txt
    bb_file = open(box, "r")  # Otworzenie pliku z którego wczytuje wszystkie dane

    lines = bb_file.read()

    file_split = lines.split("\n")

    vector_name = []
    box_dict = {}

    zmienna = os.path.join(args.data_dir, "frames") # ścieżka do pliku z zdjęciami
    img_list = os.listdir(zmienna)
    img_list.sort()

    bb_file.close() # Zamknięcie pliku z którego wczytuje wszystkie dane

    for img in img_list:
        # TODO Druga pętla jest niepotrzebna.
        for box in range(len(file_split)):
            if img == file_split[box]:
                # print(file_split[box])
                index = int(file_split[box + 1])
                img_class = write_kord(index)
                vector_name.append(file_split[box])

                if index == 0:# jeśli na zdjęciu nie ma żadnych BB, tworzy element do listy bez tych koordynatów
                    box_dict[file_split[box]] = img_class
                if index > 0:
                    for idx in range(index):# jeśli na zdjęciu są BB tworzy listę przechowująca te koordynaty
                        kordy = file_split[box + 1 + idx + 1].split(" ")
                        cords_array = [float(kordy[0]), float(kordy[1]), float(kordy[2]), float(kordy[3])]
                        # print(kordy)
                        img_class.add_box(idx, cords_array)
                        box_dict[file_split[box]] = img_class # tworzenie listy przechowującej koordynaty do BB


    numer_zdjecia = 0
    numer_histogramu = 0
    # wyświetlanie obrazów wraz z ramkami wokół ludzi


    for name in vector_name:
        img1 = cv.imread(args.data_dir + '/frames/' +name)
        # print(('\nNumer zdjecia ' + str(numer_zdjecia + 1)))

        if int(box_dict[name].number_of_bboxes) < 1: # wypisywanie pustej lini w sytuacji gdy na zdjęciu nie ma żadnych BB
            print()
        elif int(box_dict[name].number_of_bboxes) > 0:

            present_histr = [] # lista BB znajdujących się na aktualnym zdjęciu
            G = FactorGraph()

            for index_1 in range(box_dict[name].number_of_bboxes):


                first_point = (int(box_dict[name].bboxes_array[index_1, 0]) + int(box_dict[name].bboxes_array[index_1, 2]), # punky początkowy BB
                               int(box_dict[name].bboxes_array[index_1, 1]))
                last_point = (int(box_dict[name].bboxes_array[index_1, 0]),
                              int(box_dict[name].bboxes_array[index_1, 2]) + int(box_dict[name].bboxes_array[index_1, 3])) # punky końcowy BB
                # cv.rectangle(img1, first_point, last_point, (0, 0, 255), 3) #wyświetlanie podstawowego BB

                # tworzenie parametórw do zmniejszonego BB
                point_f_x, point_f_y = first_point
                point_l_x, point_l_y = last_point
                center_l_x = point_l_x + (point_f_x - point_l_x) / 2
                center_l_y = point_f_y + (point_l_y - point_f_y) / 2
                square_x = (center_l_x - point_l_x) / 2
                square_y = (center_l_y - point_f_y) / 2
                left_x = int(center_l_x - square_x)
                right_x = int(center_l_x + square_x)
                down_y = int(center_l_y - square_y)
                up_y = int(center_l_y + square_y)


                img_to_hist = img1[down_y:up_y, left_x:right_x]
                # cv.imshow('zdjecie do Histograma' + str(numer_zdjecia), img_to_hist)  #Wyświetlanie BB
                # TODO Kolorowy histogram mógłby być lepszy w tej sytuacji.
                img_to_hist = cv.cvtColor(img_to_hist, cv.COLOR_BGR2GRAY)
                histr = cv.calcHist([img_to_hist], [0], None, [256], [0, 256]) # tworzenie histogramu z zmnijeszonego BBoxa
                # plt.plot(histr)
                # plt.show()

                present_histr.append(histr) # dodanie BB do listy
                numer_histogramu += 1

                # print('Numer BB: ' + str(numer_histogramu), '\nWysokość', up_y - down_y, ' Szerokosc: ', right_x - left_x)
                # cv.rectangle(img1, (left_x, down_y), (right_x, up_y), (255, 0, 0), 2)  # wyświetlanie zmniejszonego BB

            # cv.imshow('Image' + str(numer_zdjecia + 1), img1)

            list_of_compare_hist = [] # Lista porównanych histogramów
            wartosc = []
            if numer_zdjecia <1:
                # TODO A co jeśli na 1. zdjęciu będzie więcej niż 1 BB?
                print("-1")
            if numer_zdjecia >= 1:
                for i in range(len(present_histr)):
                    DisFact_name = str(name) + '_' + str(i) # nazwa dla każdego kolejnego histogramu na aktualnym zdjęciu0
                    wartosc.append(DisFact_name)
                    G.add_node(DisFact_name)

                    for j in range(len(previos_histr)):
                        compare = cv.compareHist(present_histr[i], previos_histr[j], cv.HISTCMP_CORREL) # porównywanie histogramów z aktualnego zdjęcia oraz wcześniejszego zdjęcia
                        # print('Compare', compare)
                        # plt.subplot(1, 2, 1)
                        # plt.plot(present_histr[i])
                        # plt.subplot(1, 2, 2)
                        # plt.plot(previos_histr[j])
                        # plt.show()
                        list_of_compare_hist.append(compare)

                    phi0 = DiscreteFactor([DisFact_name], [len(previos_histr) + 1], [[0.6] + list_of_compare_hist])
                    G.add_factors(phi0)
                    G.add_edge(DisFact_name, phi0)
                    list_of_compare_hist.clear()

                A = np.ones((len(previos_histr) + 1, len(previos_histr) + 1)) # tworzenie macierzy służącej później do kombinacji w DiscreteFactor
                B = np.eye(len(previos_histr) + 1)
                AB = A - B
                AB[0][0] += 1

                comb = [x for x in combinations(wartosc, 2)] # tworzenie kombinacji pomiędzy BB na zdjęciach
                for i in list(comb):

                    # print(comb)
                    phi1 = DiscreteFactor([i[0], i[1]], [len(previos_histr) + 1, len(previos_histr) + 1], AB)
                    G.add_factors(phi1)
                    G.add_edge(i[0], phi1)
                    G.add_edge(i[1], phi1)

                Bel_Propag = BeliefPropagation(G)
                Bel_Propag.calibrate()

                result = list(Bel_Propag.map_query(show_progress=False, variables=G.get_variable_nodes()).values())
                result = [x - 1 for x in result] # zmniejszanie każdego resulta o 1

                for i in result: # wypisanie wyjścia w poprawnym formacie
                    print(i, end=" ")
                print("")


                wartosc.clear()

            previos_histr.clear()
            previos_histr = present_histr.copy()
            present_histr.clear()

            numer_zdjecia += 1
            # cv.waitKey(0)
            numer_histogramu = 0


if __name__ == '__main__':
    main()
