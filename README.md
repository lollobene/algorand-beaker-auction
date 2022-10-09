# algorand-beaker-auction

## Development Environment

### Install Sandbox

Install the [sandbox](https://github.com/algorand/sandbox) to start a local private node and start it with the `dev` configuration.

If you're in the sandbox directory run:

```bash
./sandbox up dev
```

### Clone repository

Next, clone this repository and cd to the root directory.

### Setup Virtual Environment

Create a virtual environment inside the project directory. 
#### This project requires Python 3.10.

```bash
python3 -m venv venv
```

Activate virtual environment.

```bash
source ./venv/bin/activate
```

requirements.txt file contains all of the required dependencies and packages. Install them in your virtual environment by running:

```bash
pip install -r requirements.txt
```

Check all dependencies and packages install in your virtual environment by running:

```bash
pip list
```

Run the client from auction directory
```bash
python auction.py
```