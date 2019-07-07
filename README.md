# Course_Management_Microservice

Il microservizio permette agli utenti dell'applicazione di supporto alla didattica di gestire i propri i corsi.
Nello specifico, i docenti possono:
- Creare un corso
- Creare una Prenotazione d'Esame per un Corso
- Pubblicare un Avviso per un Corso
Gli studenti possono:
- Iscriversi ad un corso
- Prenotarsi ad un esame
- Cercare un corso

Il microservizio espone un'interfaccia REST, i cui endpoint sono documentati su [SwaggerHub](https://app.swaggerhub.com/apis-docs/redefik/CourseManagement/1.0#/) e nella cartella [api](api/).

## Linguaggio
Python

## Strato di persistenza
MongoDB
