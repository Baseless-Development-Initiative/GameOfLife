
# Run from this directory only

cd ..
pip install -r requirements.txt

# Install game and create distribution directory
pyinstaller game_of_life.py

# Copy game icon svg
cp -r _static dist/game_of_life/_internal/_static
