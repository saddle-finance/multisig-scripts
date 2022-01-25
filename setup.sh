echo "\n** Installing dependencies..."
python3 -m pip install --user pipx && python3 -m pipx ensurepath
mkvenv --python=3.9.9
pip install --no-deps -r requirements.txt

echo "\n** Creating config files..."
cp -R .brownie ~/

echo "\n** Creating .env from template - don't forget to add your API key!"
cp .env.template .env

echo "\n** Please supply the DEPLOYER ACCOUNT's private key when prompted."
brownie accounts new deployer