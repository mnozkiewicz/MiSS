# Sensor Placement Problem

## dataset

> np.Hanoi

>ustalona liczba sensorów

## działanie symulacji

> przyjmuje estymaty zapotrzebowań na wodę

> zwraca estymaty ciśnień

> pomiary w węzłach

> nie mamy danych prawdziwych - zamiast nich dodajemy wyciej jako zwiększone zapotrzebowanie

> zakładamy tylko jeden wyciek

## klasyfikator
> kNN - n sąsiadów / metryka (zrobić z KNN regresję???)

> działa na różnicach (residuals) pomiędzy przewidywaniami, a rzeczywistymi danymi

## optymalizacja

> minimalizujemy funkcję kosztu - leak location error - pomyłka odległości -liczona alg. Floyda-Warshalla

> symulowane wyżarzanie -proponowane (czy coś innego???)