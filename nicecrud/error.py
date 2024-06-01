from nicegui import ui


# TODO: Use modularization https://github.com/zauberzeug/nicegui/blob/main/examples/modularization/message.py to show the error
def show_error(message: str = "Somethin went horribly wrong"):
    with ui.row().classes("align-center") as row_element:
        with ui.grid(columns="max-content 1fr").classes(
            "gap-0 text-red-500 bg-yellow-100 border-l-8 border-yellow-500 p-1 align-center items-center"
        ):
            ui.icon("error", size="lg").classes("p-2")
            label_element = ui.label(message).classes("pl-0 pr-3 font-bold")
    return label_element, row_element


def show_warn(message: str = "Somethin went not quite horribly wrong"):
    with ui.row().classes("gap-3 text-orange-500 bg-white border-l-4 border-orange-500 p-4"):
        ui.icon("warning")
        ui.label(message)


if __name__ == "__main__":
    show_error()
