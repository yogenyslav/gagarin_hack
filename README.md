# 🚀 Гагарин Hack 
## 🙋🏻‍♂️ Решение команды МИСИС Либа Справа 2 Этаж

## 🪐 Кейс Юпитер. Сервис для анализа видеопотока на наличие аномалий

### О сервисе

Сервис позволяет загрузить данные в произвольном формате, получить визуализированную статистику по задетектированным аномалиям и выгрузить отчет об аномалиях в csv-файл 

#### Ссылка на сервис - 
#### Демонстрация работы - 
#### Архитектура

### How to use guide:

1. Выберите режим
    - *анализ байтового потока* (время обработки 1 кадра - , accuracy - )
    - *анализ в формате RGB* (время обработки 1 кадра - , accuracy - )
4. Загрузите *.mp4* файл, или *zip-архив* с файлами .mp4, или ссылку на *rtsp поток*
5. В случае загрузки *zip-архива* выберите файлы для построения графиков и отчета (или укажите *все*) и дождитесь окончания обработки
6. В случае загрузки ссылки на *rtsp поток* выберите момент остановки чтения потока. Отчет составится на основании промежутка с начала чтения потока до завершения
7. Скачайте отчёт (формат - .csv)
8. Структура отчета:
    - Секунда, на которой произошла аномалия
    - Тип аномалии (Размытие, Свет, Перекрытие, Движение)
    - Ссылка на соответствующий кадр

### Архитектура ML

*Анализ байтового потока:*  
Видео в .mp4 ➡️ перевод в байты ➡️ feature engineering ➡️ CatBoostClassifier ➡️ вероятность каждой аномалии

*Анализ в формате RGB:*  
Видео в .mp4 ➡️ Кадры в RGB ➡️ ResNet18 ➡️ вероятность каждой аномалии

