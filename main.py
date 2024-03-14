from gui.main_gui import GUIClass
from etl.main_etl import ETLClass
import ttkbootstrap as tb

if __name__ == "__main__":
    root = tb.Window(themename='superhero')
    root.protocol('WM_DELETE_WINDOW', root.destroy)

    # Crie primeiro a instância da ETLClass
    etl = ETLClass()

    # Em seguida, crie a instância da GUIClass, passando a instância etl como parâmetro
    gui = GUIClass(root, etl)

    # Configure a instância da ETLClass para conter uma referência à instância da GUIClass
    etl.set_gui(gui)

    # Inicie a interface gráfica
    root.mainloop()
