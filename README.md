# Participation pipeline

## Installation

The following steps are the installation guide:

### 1. Clone the repository

The repository can be cloned via `ssh` or `https`. It is recommended to clone it via ssh, following the [GitLab `ssh` key management](https://docs.gitlab.com/ee/ssh/), from the GSI network. In case you are not connected to the GSI network, it will be necessary to clone it by `https`.

```zsh
# SSH
git clone --recurse-submodules -j8 ssh://git@lab.gsi.upm.es:2200/participation/participation-pipeline.git
# HTTPS
git clone --recurse-submodules -j8 https://lab.gsi.upm.es/participation/participation-pipeline.git
```

In case the submodules have not been updated correctly, an update of the local repository is required with the following command:

```zsh
git submodule update --remote
```

### 2. Set environment variables

The pipeline requires the following environment variables:

- For GSICrawler (in the gsicrawler/.env file):

```
TWITTER_CONSUMER_KEY=
TWITTER_CONSUMER_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=

DISCORD_TOKEN=

FACEBOOK_USER=
FACEBOOK_PASSWORD=
```

- For the pipeline itself (in the .env file):

```
GOOGLE_API_KEY=

GSICRAWLER_URL=http://gsicrawler:5000/api/v1
SENPY_URL=http://senpy:5000/api/

FUSEKI_URL=fuseki
FUSEKI_PORT=3030

ES_URL=elasticsearch
ES_PORT=9200
ELASTIC_VERSION=7.12.0

ES_USER=elastic
ES_PASSWORD=
```

### 3. Add LIWC and MFT dictionaries

Another requirement of the pipeline is to have the LIWC dictionaries, inside the `senpy-plugins/data/` folder:

```
LIWC2015Dictionary-en.dic
LIWCDictionary-de.dic
LIWCDictionary-en.dic
LIWCDictionary-en.dic
MFTDictionary-de.dic
```

### 4. Execute the pipeline

There are example scripts in the app/scripts/example directory to execute the pipeline for different sources.

There is also a capture_twitter.py script to search for all the hashtags in the config/hashtags.json file.

---
# Participation pipeline

## Instalación

Los siguientes pasos sirven de guía de instación:

### 1. Clonar el repositorio

El repositorio se puede clonar mediante `ssh` o `https`. Se recomienda clonarlo mediante ssh, siguiendo la [gestión de claves `ssh` de GitLab](https://docs.gitlab.com/ee/ssh/), desde la red del GSI. En caso de no estar conectado en la red del GSI, será necesario clonarlo por `https`.

```zsh
# SSH
git clone --recurse-submodules -j8 ssh://git@lab.gsi.upm.es:2200/participation/participation-pipeline.git
# HTTPS
git clone --recurse-submodules -j8 https://lab.gsi.upm.es/participation/participation-pipeline.git
```

En caso de que no se hayan actualizado correctamente los sumódulos, se requiere una actualización del repositorio local con el siguiente comando:

```
git submodule update --remote
```

### 2. Configurar variables de entorno

La pipeline requiere las siguientes variables de entorno:

- Para GSICrawler (en el archivo gsicrawler/.env):

```
TWITTER_CONSUMER_KEY=
TWITTER_CONSUMER_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=

DISCORD_TOKEN=

FACEBOOK_USER=
FACEBOOK_PASSWORD=
```

- Para la propia pipeline (en el archivo .env):

```
GOOGLE_API_KEY=

GSICRAWLER_URL=http://gsicrawler:5000/api/v1
SENPY_URL=http://senpy:5000/api/

FUSEKI_URL=fuseki
FUSEKI_PORT=3030

ES_URL=elasticsearch
ES_PORT=9200
ELASTIC_VERSION=7.12.0

ES_USER=elastic
ES_PASSWORD=
```

### 3. Añadir diccionarios LIWC y MFT

Otro requisito de la pipeline es tener los diccionarios de LIWC, dentro de la carpeta de `senpy-plugins/data/`:

```
LIWC2015Dictionary-en.dic
LIWCDictionary-de.dic
LIWCDictionary-en.dic
LIWCDictionary-es.dic
MFTDictionary-de.dic
```

### 4. Ejecutar la pipeline

Hay ejemplos de scripts en el directorio app/scripts/example que ejecutan la pipeline para diferentes fuentes.

Hay también un script capture_twitter.py para buscar todos los hashtags del archivo config/hashtags.json.