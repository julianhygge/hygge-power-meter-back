import schedule
import time
from datetime import datetime, timedelta

from hyggepowermeter.utils.logger import logger


class StuderDataProcessor:
    def __init__(self, db_client):
        self.__db_client = db_client

    def get_daily_pv_generations(self):
        inverter_1_id: int = 4
        inverter_2_id: int = 5
        # variotracks id in meghalaya
        box_id = "meghalaya"
        self.get_pv_generation_by_box_and_device_id(box_id, inverter_1_id)
        self.get_pv_generation_by_box_and_device_id(box_id, inverter_2_id)
        logger.info("Daily pv generation inserted in daily database")

    def get_pv_generation_by_box_and_device_id(self, box_id, device_id):
        since_date = datetime.min
        last_date = self.__db_client.select_last_daily_generation(box_id, device_id)
        if any(last_date):
            since_date = last_date[0].measurement_date
        results = self.__db_client.select_pv_generations_by_day_after_date(since_date, device_id)
        grouped_results = {}
        list_results = list(results)
        for result in list_results:
            date = datetime.date(result.timestamp)
            year, month, day = date.year, date.month, date.day
            key = (year, month, day)
            if key not in grouped_results:
                grouped_results[key] = []
            grouped_results[key].append(result)
        daily_productions = []
        for group in grouped_results.values():
            first_result = group[0]
            day_before = first_result.timestamp - timedelta(days=1)
            daily_productions.append({
                'id': first_result.id,
                'timestamp': day_before,
                'vt_prod_pre_day_kwh': first_result.vt_prod_pre_day_kwh,
                'device_id': first_result.device_id
            })
        daily_productions_sorted = sorted(daily_productions, key=lambda x: x['timestamp'])
        production_entities = []
        for d in daily_productions_sorted:
            production_entities.append(
                {
                    'measurement_date': d['timestamp'].date(),
                    'kwh': d['vt_prod_pre_day_kwh'],
                    'device_id': d['device_id'],
                    'box_id': box_id
                })
        self.__db_client.insert_daily_production(production_entities)

    def process_studer_data(self):
        self.get_daily_pv_generations()
        schedule.every().day.at("23:00").do(self.get_daily_pv_generations)
        schedule.every().day.at("01:00").do(self.get_daily_pv_generations)

        while True:
            schedule.run_pending()
            time.sleep(60)
