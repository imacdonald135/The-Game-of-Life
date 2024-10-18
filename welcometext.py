from pyfiglet import Figlet

class WelcomeText:
    def __init__(self):
        f = Figlet(font='lean')
        text1 = f.renderText('Game of')
        text2 = f.renderText('Life')
        text1lines = text1.splitlines()
        text2lines = text2.splitlines()
        final = []
        for i in range(len(text1lines)):
            final.append(text1lines[i] + text2lines[i])
        self.textlines = final



    def print(self):
        for line in self.textlines:
            print(line)




# def main():
#     w = WelcomeText()
#     print(len(w.textlines))
#
# main()