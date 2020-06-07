from lifxlan import LifxLAN


class ReturnConnectedLightsViaName:
    def __init__(self, device_list: list) -> list:
        """
        -- MUST UTILISE WITH --
        returns a list of connection objects - i.e. requested lifx bulb(s)

        Args:
            device_list (list): Names of bulb(s)

        Returns:
            list: list of connection objects
        """
        self.device_list = device_list

    def __enter__(self):
        self.connection = LifxLAN(len(self.device_list))
        return self.connection.get_devices_by_name(self.device_list)

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.connection