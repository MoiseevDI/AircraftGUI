import json
import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime, time as dtime, timedelta
from tkinter import messagebox, StringVar
from Aircraft import AircraftLibInitClass


COLUMNS = ["Airplane_ID", "Departure_point", "Arrive_point", "Start_day", "End_day", "Start_Time", "End_Time"]


class MainPage(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_container = tk.Frame(self)

        waypoint_container = tk.Frame(self.data_container)
        waypoint_container.pack(side=tk.RIGHT, fill=tk.BOTH)
        waypoint_label = tk.Label(waypoint_container, text="Waypoints")
        waypoint_label.pack()
        self.waypoints = tk.Listbox(waypoint_container)
        self.waypoints.pack(fill=tk.BOTH, expand=True)

        self.button_container = tk.Frame(self)
        self.button_container.pack(side=tk.LEFT, fill=tk.Y)

        self.api = AircraftLibInitClass()
        self.process_table()
        self.process_buttons()

    def __process_filter(self):
        value = self.entry.get()
        if value.isdigit():
            self.fill_tree(int(value))
        else:
            messagebox.showwarning(message="Airplane ID for filter must be a digit")

    def process_buttons(self):
        entry_label = tk.Label(self.button_container, text="Airplane ID")
        entry_label.pack()
        self.entry = ttk.Entry(self.button_container)
        self.entry.pack(side=tk.TOP)
        filter_button = ttk.Button(self.button_container, text='Filter by ID',
                                command=lambda: self.__process_filter(),
                                compound=tk.TOP, cursor='hand2')
        filter_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        drop_filter_button = ttk.Button(self.button_container, text='Remove filter',
                                command=lambda: self.fill_tree(),
                                compound=tk.TOP, cursor='hand2')
        drop_filter_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        add_flight_button = ttk.Button(self.button_container, text='Add flight',
                                command=lambda: FlightPage(self),
                                compound=tk.TOP, cursor='hand2')
        add_flight_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        add_waypoint_button = ttk.Button(self.button_container, text='Add waypoint',
                                command=lambda: WaypointPage(self),
                                compound=tk.TOP, cursor='hand2')
        add_waypoint_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        airtime_button = ttk.Button(self.button_container, text='Compute airtime',
                                command=lambda: self.compute_airtime(),
                                compound=tk.TOP, cursor='hand2')
        airtime_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        fastest_route_button = ttk.Button(self.button_container, text='Fastest route',
                                command=lambda: RoutePage(self),
                                compound=tk.TOP, cursor='hand2')
        fastest_route_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH)



    def process_table(self):
        x_scroll = tk.Scrollbar(self.data_container, orient='horizontal', cursor='hand2')
        y_scroll = tk.Scrollbar(self.data_container, orient='vertical', cursor='hand2')

        self.tree_view = ttk.Treeview(
            self.data_container,
            columns=COLUMNS,
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set,
        )
        self.tree_view["show"] = "headings"
        for field in COLUMNS:
            self.tree_view.heading(field, text=field.capitalize())

        x_scroll.config(command=self.tree_view.xview)
        y_scroll.config(command=self.tree_view.yview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_view.pack(side=tk.LEFT, fill=tk.BOTH)
        self.data_container.pack(side=tk.LEFT, fill=tk.Y)


    def fill_tree(self, airplane_id: int = None):
        self.tree_view.delete(*self.tree_view.get_children())
        retrieved_data = self.api.getTimeTableForPlane(airplane_id) if airplane_id else self.api.getTimetable()
        for ind, way in enumerate(retrieved_data):
            values = [way.airplaneId, way.startPoint, way.endPoint, way.startWeekDay, way.endWeekDay, way.startTime, way.endTime]
            self.tree_view.insert(parent="", index=ind, values=values)

    def add_waypoint(self, waypoint):
        self.waypoints.insert(tk.END, waypoint)

    def compute_airtime(self):
        selected_item = self.tree_view.selection()
        if len(selected_item) == 1:
            data = self.tree_view.item(selected_item)["values"]
            diff = self.api.getPlaneAirTime(int(data[0]))
            messagebox.showinfo(message=str(dtime(hour=diff // 3600, minute=diff // 60, second=diff % 60)))
        else:
            messagebox.showwarning(message="Select one item, then compute a time")


class FlightPage(tk.Tk):

    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root
        self.entry_container = tk.Frame(self)
        self.entry_container.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.button_container = tk.Frame(self)
        self.button_container.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.labels = tk.Frame(self)
        self.labels.pack(side=tk.LEFT, fill=tk.BOTH)
        self.process_entries()
        self.process_buttons()

    def insert_flight(self):
        try:
            self.root.api.addFlight(
                int(self.airplane_id.get()),
                self.departure.get(),
                self.arrive.get(),
                int(self.start_day.get()),
                int(self.end_day.get()),
                int(self.start_time.get()),
                int(self.end_time.get())
                )
            self.destroy()
            self.root.fill_tree()
        except RuntimeError as exc:
            messagebox.showerror(message=str(exc))
        except ValueError:
            messagebox.showerror(message="Departure and arrive points muste be strings, other data must be integer")


    def process_entries(self):
        self.airplane_id = ttk.Entry(self.entry_container)
        self.airplane_id.pack()
        airplane_label = tk.Label(self.labels, text="Airplane ID")
        airplane_label.pack()

        self.departure = ttk.Entry(self.entry_container)
        self.departure.pack()
        departure_label = tk.Label(self.labels, text="Departure point")
        departure_label.pack()

        self.arrive = ttk.Entry(self.entry_container)
        self.arrive.pack()
        arrive_label = tk.Label(self.labels, text="Arrive point")
        arrive_label.pack()

        self.start_day = ttk.Entry(self.entry_container)
        self.start_day.pack()
        start_day_label = tk.Label(self.labels, text="Start day")
        start_day_label.pack()

        self.end_day = ttk.Entry(self.entry_container)
        self.end_day.pack()
        end_day_label = tk.Label(self.labels, text="End day")
        end_day_label.pack()

        self.start_time = ttk.Entry(self.entry_container)
        self.start_time.pack()
        start_time_label = tk.Label(self.labels, text="Start timestamp")
        start_time_label.pack()

        self.end_time = ttk.Entry(self.entry_container)
        self.end_time.pack()
        end_time_label = tk.Label(self.labels, text="End timestamp")
        end_time_label.pack()

    def process_buttons(self):
        back_button = ttk.Button(self.button_container, text='Back',
                                command=lambda: self.destroy(),
                                compound=tk.BOTTOM, cursor='hand2')
        back_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        apply_button = ttk.Button(self.button_container, text='Apply',
                                command=lambda: self.insert_flight(),
                                compound=tk.BOTTOM, cursor='hand2')
        apply_button.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)


class WaypointPage(tk.Tk):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root
        entry_container = tk.Frame(self)
        entry_container.pack(side=tk.TOP, fill=tk.BOTH)

        label = tk.Label(entry_container, text="Absolute path to json file")
        label.pack(side=tk.LEFT)

        self.json_entry = ttk.Entry(entry_container)
        self.json_entry.pack(side=tk.RIGHT)

        button_container = tk.Frame(self)
        button_container.pack(side=tk.BOTTOM, fill=tk.BOTH)

        back_button = ttk.Button(button_container, text='Back',
                                command=lambda: self.destroy(),
                                compound=tk.BOTTOM, cursor='hand2')
        back_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        load_button = ttk.Button(button_container, text='Add waypoint',
                                command=lambda: self.add_waypoint(),
                                compound=tk.BOTTOM, cursor='hand2')
        load_button.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def add_waypoint(self):
        try:
            with open(self.json_entry.get(), "r") as f:
                data = json.load(f)
                self.root.api.addDestination(
                    data["name"],
                    data["ways"]
                )
            self.root.add_waypoint(data["name"])
            self.destroy()
        except FileNotFoundError:
            messagebox.showerror(message="File not found")
        except RuntimeError:
            messagebox.showerror(message="Invalid data format")


class RoutePage(tk.Tk):
    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root
        entry_container = tk.Frame(self)
        entry_container.pack(side=tk.RIGHT, fill=tk.BOTH)
        button_container = tk.Frame(self)
        button_container.pack(side=tk.BOTTOM, fill=tk.BOTH)
        label_container = tk.Frame(self)
        label_container.pack(side=tk.LEFT, fill=tk.BOTH)

        start_label = tk.Label(label_container, text="Departure")
        start_label.pack()
        self.start_entry = ttk.Entry(entry_container)
        self.start_entry.pack()

        end_label = tk.Label(label_container, text="Arrive")
        end_label.pack()
        self.end_entry = ttk.Entry(entry_container)
        self.end_entry.pack()

        time_label = tk.Label(label_container, text="Time")
        time_label.pack()
        self.time_entry = ttk.Entry(entry_container)
        self.time_entry.pack()

        

        back_button = ttk.Button(button_container, text='Back',
                                command=lambda: self.destroy(),
                                compound=tk.BOTTOM, cursor='hand2')
        back_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        load_button = ttk.Button(button_container, text='Compute',
                                command=lambda: self.compute_route(),
                                compound=tk.BOTTOM, cursor='hand2')
        load_button.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def compute_route(self):
        def __route_view(route_list):
            return "\n".join([f"Flight {item.startPoint} -> {item.endPoint}, Time: {item.startTime}" for item in route_list])
        try:
            fastest_route_list = self.root.api.getFastestRoute(
                self.start_entry.get(),
                self.end_entry.get(),
                int(self.time_entry.get())
            )
            messagebox.showinfo(message=__route_view(fastest_route_list))
        except RuntimeError as exc:
            messagebox.showerror(message=str(exc))


if __name__ == "__main__":
    root = MainPage()
    root.mainloop()