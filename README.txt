w celu uruchomienia programu należy podać ścieżke do foldera(c6s1) w którym znajduja się folder 
z zdjęciami oraz plik txt zawierający nazwę zdjęcia w folderze, ilosć BB na danym zdjęciu oraz 
współrzędne BB na zdjęciu.

Program służący do śledzenie przechodniów wykorzystuje biblioteke pgmpy (Factor Graph, 
DiscreteFactor, BelifPropagation), która służa do tworzenia propabilistycznych modeli grafowych.
Modele te są na początku wczytywane, a potem po kolei przetwarzane i tworzone są bounding boxy
na każdym kolejnym zdjęciu. Pole BB zostaje zmniejszone 4 krotnie w celu większej precyzji, 
a następnie tworzone są histogramy z każdego zmniejszonego BB. Modele grafowe tworzone są na 
podstawie stopnia podobieństwa histogramu z aktualnego zdjęcia do histogramów z wcześniejszego 
zdjęcia. Dla każdego zdjęcia tworzy się model grafowy. Zmiennymi losowymi są podstawowe prostokąty 
ograniczające, które łącza się z czynnikiem określającym prawdopodobieństwo porównania osób z
zdjęcia aktualnego do zdjęcia poprzedniego. W celu uniknięcia możliwości przydzielenia większej
ilości osób, z aktualnego zdjęcia do zdjęcia wcześniejszego stworzone są połączenia, czynniki
łączące wypełniane są w sposób jak na zdjęciu(zdjecie.png)



