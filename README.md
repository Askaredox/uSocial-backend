* sudo docker-compose -f "docker-compose.yaml" down
* sudo docker-compose -f "docker-compose.yaml" up -d --build
|Ruta		        	|Metodo	  	      |		           |	
| ----------- 		| ------------- 	|------------	|
|/usuarios	     |	GET	          	|ninguno	     |
|/usuarios/new		|      POST	  	  |{"Nombre":string,"Usuario":string,"Contrasenia":string,"Confirmacion":string,"Foto":{"base64":string,"ext":string},"ModoBot":bool,"Amigos":[strings]}		|
|/login		      	|      POST		  |{"Usuario":string,"Contrasenia":string}		|
|/usuarios/add		|      POST	  	|{"Usuario":string,"Amigo":string user del nuevo amigo}		|
|/posts		      	|      GET	   	|Ninguno	|
|/posts/new	   	|      POST	  	|{"Image":string,"Text":string,"User":string quien publica,"Tags":[strings]}		|
|/posts/home	  	|      GET	  	 |User=...	|		
|/posts/filtrar	|      GET	  	 |User=...&Tag=...|
|/usuarios/modify|      PUT      | {"Nombre":string,"Usuario":string,"Foto":{"base64":string,"ext":string},"ModoBot":bool}


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

## Como usar init.sh y start.sh

### init.sh

Primero creas un archivo llamado init.sh:

```$ nano init.sh```

Copias y pegas el contenido de init.sh del repositorio dentro de este archivo y le das `ctrl+x` y enter. 

Luego le agregas permisos de ejecución:

```$ chmod +x init.sh```

Y finalmente ejecutas el archivo:

```$ ./init.sh```

Y esperas a que se instale todo y lo corra

SOLO PARA LA PRIMERA VEZ QUE INICIAS UNA MAQUINA

### start.sh

Agregas los permisos de ejecución:

```$ chmod +x start.sh```

Y finalmente ejecutas el archivo:

```$ ./start.sh```

Esperas a que corra docker compose

USAR CADA VEZ QUE ENCIENDES LA MAQUINA DESPUES DE LA PRIMERA VEZ
