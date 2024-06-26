from nicegui import ui


def show_error(message: str = "Somethin went horribly wrong"):
    with ui.row().classes(
        "align-center text-red-500 bg-yellow-100 items-center gap-2 flex-nowrap"
    ) as row_element:
        ui.icon("error", size="lg").classes("p-2 border-l-8 border-yellow-500 ")
        label_element = ui.label(message).classes("pl-0 pr-3 font-bold")
    return label_element, row_element


def show_warn(message: str = "Something went not quite as horribly wrong, but still not good"):
    with ui.row().classes("gap-3 text-orange-500 bg-white border-l-4 border-orange-500 p-4"):
        ui.icon("warning")
        ui.label(message)


if __name__ == "__main__":
    show_error()
    ui.run()
