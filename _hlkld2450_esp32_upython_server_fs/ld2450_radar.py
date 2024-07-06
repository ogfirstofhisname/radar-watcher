
class HLKLD2450Radar():
    def __init__(self):
        pass

    def read_single_radar_data(self):
        '''
        Reads without parsing a single 'row' of radar data.

        Returns:
        radar_data: bytes, the radar data read
        '''
        pass

    def parse_radar_data(self, radar_data):
        '''
        A convenience method to parse the radar data into a dictionary of target values.
        Not used in the server-client implementation.
        Adapted to micropython from https://github.com/csRon/HLK-LD2450.

        Args:
        radar_data: bytes, a single 30-byte read from the radar sensor

        Returns:
        target_values: dict, a dictionary of target values
        '''
        pass