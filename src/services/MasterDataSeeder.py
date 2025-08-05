import logging
import random
from datetime import datetime, time
from typing import List
from src.models.users.Master import Master
from src.repository.MasterRepository import MasterRepository

logger = logging.getLogger(__name__)


class MastersDataSeeder:
    """Класс для заполнения базы данных мастерами салона красоты"""

    def __init__(self, master_repository: MasterRepository):
        self.master_repo = master_repository

    async def seed_all_masters(self):
        """Добавляет всех мастеров в базу данных"""
        try:
            logger.info("Начинаем добавление мастеров в базу данных...")

            # Получаем все данные о мастерах
            all_masters_data = self._get_all_masters_data()

            added_count = 0
            skipped_count = 0

            for master_data in all_masters_data:
                try:
                    # Проверяем, существует ли уже такой мастер по username
                    existing_master = await self.master_repo.get_by_telegram_id(master_data['telegram_id'])

                    if existing_master:
                        logger.info(f"Мастер с username '{master_data['username']}' уже существует, пропускаем")
                        skipped_count += 1
                        continue

                    # Создаем объект мастера
                    master = Master(
                        telegram_id=master_data.get('telegram_id'),
                        username=master_data['username'],
                        name=master_data['name'],
                        phone=master_data.get('phone'),
                        email=master_data.get('email'),
                        specialization=master_data['specialization'],
                        experience_years=master_data['experience_years'],
                        rating=master_data['rating'],
                        is_active=True,
                        # Преобразуем строки в объекты time
                        working_hours_start=datetime.strptime(master_data['working_hours_start'], '%H:%M').time(),
                        working_hours_end=datetime.strptime(master_data['working_hours_end'], '%H:%M').time(),
                        working_days=master_data['working_days'],
                        service_ids=master_data.get('service_ids', [])
                    )

                    # Добавляем в базу данных
                    created_master = await self.master_repo.create(master)
                    logger.info(f"Добавлен мастер: {created_master.name} (ID: {created_master.id}, Специализация: {created_master.specialization})")
                    added_count += 1

                except Exception as e:
                    logger.error(f"Ошибка при добавлении мастера '{master_data.get('name')}': {e}")
                    continue

            logger.info(f"✅ Завершено! Добавлено: {added_count}, пропущено: {skipped_count}")

        except Exception as e:
            logger.error(f"Ошибка при заполнении мастеров: {e}")
            raise

    def _get_all_masters_data(self) -> List[dict]:
        """Возвращает данные 30 мастеров с рандомными service_id"""
        masters_data = []

        # Списки для генерации рандомных данных
        specializations = [
            "hair_services", "cosmetology", "nails_services", "hardware_services",
            "makeup_services", "brows_lashes_services", "spa_services",
            "kids_services", "women_haircut", "men_haircut", "kids_haircut",
            "blow_dry", "festive_styling", "evening_styling", "single_color",
            "highlights", "coloring", "ombre_shatush", "balayage", "toning",
            "hair_botox", "keratin_treatment", "hair_lamination", "treatment_masks",
            "capsule_extension", "tape_extension", "weft_extension", "perm",
            "hair_care", "beard_styling", "wedding_hairstyle", "hollywood_curls",
            "creative_coloring", "chemical_straightening", "hot_scissors",
            "hair_glazing", "hair_screening", "hair_polishing", "manual_cleaning",
            "ultrasonic_cleaning", "vacuum_cleaning", "combined_cleaning",
            "chemical_peeling", "mechanical_peeling", "enzyme_peeling",
            "gas_liquid_peeling", "alginate_mask", "collagen_mask",
            "moisturizing_mask", "cleansing_mask", "anti_aging_mask",
            "classic_face_massage", "lymphatic_massage", "sculptural_massage",
            "gua_sha_massage", "moisturizing_care", "rejuvenating_care",
            "problem_skin_care", "soothing_care", "darsonvalization",
            "microcurrent_therapy", "rf_lifting", "mesotherapy", "biorevitalization",
            "contour_plastic", "cryotherapy", "photorejuvenation", "plasma_therapy",
            "classic_manicure", "european_manicure", "hardware_manicure",
            "spa_manicure", "mens_manicure", "classic_pedicure", "hardware_pedicure",
            "spa_pedicure", "medical_pedicure", "gel_polish", "french_manicure",
            "nail_ombre", "gel_extension", "acrylic_extension", "polygel_extension",
            "nail_art", "stamping", "nail_molding", "nail_decoration",
            "hand_paraffin", "foot_paraffin", "ingrown_nail_treatment",
            "nail_strengthening", "shape_correction", "japanese_manicure",
            "biogel_coating", "wedding_nail_design", "nail_gradient", "nail_inlay",
            "nail_rub", "laser_depilation", "photo_depilation", "elos_depilation",
            "electro_epilation", "cryolipolysis", "cavitation", "pressotherapy",
            "myostimulation", "laser_rejuvenation", "diamond_dermabrasion",
            "carbon_peeling", "radiowave_lifting", "hydro_peeling", "thermage",
            "smas_lifting", "day_makeup", "evening_makeup", "wedding_makeup",
            "photo_makeup", "special_occasion_makeup", "makeup_lessons",
            "makeup_correction", "smokey_eyes", "nude_makeup", "mature_makeup",
            "brow_tweeze", "brow_wax", "brow_architecture", "brow_tinting",
            "brow_henna", "brow_biotattoo", "brow_lamination", "brow_styling",
            "classic_lash_extension", "2d_lash_extension", "3d_lash_extension",
            "volume_lash_extension", "hollywood_volume", "lash_lamination",
            "lash_botox", "lash_tinting", "lash_perm", "lash_removal",
            "body_wraps", "body_scrub", "full_body_massage", "anti_cellulite_massage",
            "relaxing_massage", "sports_massage", "honey_massage", "hot_stone_massage",
            "hydromassage", "aromatherapy", "salt_baths", "herbal_baths",
            "milk_baths", "spa_rituals", "decollete_treatments",
            "kids_haircut_under5", "kids_haircut_5to12", "teen_haircut",
            "kids_styling", "kids_manicure", "kids_body_art", "hair_chalk",
            "hair_glitter", "face_painting", "kids_makeup"
        ]
        first_names = [
            "Александра", "Екатерина", "Мария", "Анна", "Ольга", "Елена", "Наталья", "Светлана", "Юлия", "Татьяна",
            "Иван", "Алексей", "Дмитрий", "Сергей", "Андрей", "Михаил", "Николай", "Павел", "Владимир", "Максим"
        ]
        last_names = [
            "Иванова", "Петрова", "Сидорова", "Кузнецова", "Смирнова", "Васильева", "Михайлова", "Федорова", "Соколова",
            "Попова",
            "Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов", "Васильев", "Михайлов", "Федоров", "Соколов", "Попов"
        ]

        for i in range(1, 31):
            # Выбираем случайную специализацию и имя
            specialization = random.choice(specializations)
            name = f"{random.choice(first_names)} {random.choice(last_names)}"

            # Генерируем рандомные данные
            username = f"master_{i}"
            telegram_id = 1000 + i
            experience_years = random.randint(1, 20)
            rating = round(random.uniform(3.5, 5.0), 1)

            # Генерируем рандомные рабочие часы
            start_hour = random.randint(8, 12)
            end_hour = random.randint(17, 21)
            working_hours_start = f"{start_hour:02d}:00"
            working_hours_end = f"{end_hour:02d}:00"

            # Генерируем рандомные рабочие дни (от 3 до 7 дней в неделю)
            all_days = [1, 2, 3, 4, 5, 6, 7]
            random.shuffle(all_days)
            working_days = ",".join(map(str, sorted(all_days[:random.randint(3, 7)])))

            # Генерируем рандомный список service_ids
            num_services = random.randint(3, 10)
            service_ids = random.sample(range(1, 121), num_services)

            master = {
                'telegram_id': telegram_id,
                'username': username,
                'name': name,
                'phone': None,  # Телефон можно оставить None или генерировать
                'email': None,  # Почту можно оставить None или генерировать
                'specialization': specialization,
                'experience_years': experience_years,
                'rating': rating,
                'working_hours_start': working_hours_start,
                'working_hours_end': working_hours_end,
                'working_days': working_days,
                'service_ids': service_ids
            }
            masters_data.append(master)

        return masters_data