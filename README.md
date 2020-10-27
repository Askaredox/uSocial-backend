* sudo docker-compose -f "docker-compose.yaml" down
* sudo docker-compose -f "docker-compose.yaml" up -d --build

|Ruta			|Metodo	  	|		|	
| ----------- 		| ------------- 	|------------	|
|/usuarios	      	|	GET	  	|ninguno	|
|/usuarios/new		|      POST	  	|{"Nombre":string,"Usuario":string,"Contrasenia":string,"Foto":string,"ModoBot":bool,"Amigos":[strings]}		|
|/login			|      POST		|{"Usuario":string,"Contrasenia":string}		|
|/usuarios/add		|      POST	  	|{"Usuario":string,"Amigo":string user del nuevo amigo}		|
|/posts			|      GET	  	|Ninguno	|
|/posts/new		|      POST	  	|{"Image":string,"Text":string,"User":string quien publica,"Tags":[strings]}		|
|/posts/home		|      GET	  	|User=...	|		
|/posts/filtrar	|      GET	  	|User=...&Tag=...|


ejemplo de documentos de cada colección
User
----
{
 
    "Nombre": "Andres Esteban",
    "Usuario": "Askar",
    "Contrasenia": 	"d033e22ae348aeb5660fc2140aec35850c4da997",
    "Foto": "",
    "ModoBot": true,
    "Amigos": ["Guiss097", "Gris0407"]
}

Post
----
{

    "Image": "",
    "Text": "publicacion 1",
    "Date": "",
    "Hour": "",
    "User": "Askar",
    "Tags": ["Flores", "Campo", "Carro"]
}