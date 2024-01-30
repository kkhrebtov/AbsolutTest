import datetime

import pytest
from playwright.sync_api import expect

from Pages.new_polis_step_1 import NewPolisStep1, PolisAmount
from Pages.new_polis_step_2 import NewPolisStep2
from Tests.formatter import format_dictionary_test_id


@pytest.mark.parametrize("polis_data", [
    {"polis_amount": PolisAmount.POLIS_100_000,
     "exp_cost": "1 500 ₽"},
    {"polis_amount": PolisAmount.POLIS_500_000,
     "exp_cost": "5 000 ₽"}
])
def test_polis_calculation_for_non_medic(page, polis_data):
    """Проверяем что предварительная сумма премии и срок страхования вычисляются правильно"""

    new_polis_page_1 = NewPolisStep1(page)
    if polis_data["polis_amount"] == PolisAmount.POLIS_100_000:
        new_polis_page_1.select_polis_amount(polis_data["polis_amount"])

    new_polis_page_1.check_no_virus_contact()
    new_polis_page_1.check_agreement()

    new_polis_page_1.validate_polis_cost(polis_data["exp_cost"])

    exp_start_date = (datetime.datetime.today() + datetime.timedelta(days=15)).strftime("%d.%m.%Y")
    exp_end_date = (datetime.datetime.today() + datetime.timedelta(days=366 + 15)).strftime("%d.%m.%Y")

    new_polis_page_1.validate_polis_start_date(exp_start_date)
    new_polis_page_1.validate_polis_end_date(exp_end_date)


def test_polis_creation_for_medic(page):
    """Для страхователя являющегося медиком. програма страхования недоступна"""

    new_polis_page_1 = NewPolisStep1(page)

    new_polis_page_1.check_is_medic()
    new_polis_page_1.check_no_virus_contact()
    new_polis_page_1.check_agreement()
    expect(new_polis_page_1.medicine_info).to_be_visible()
    expect(new_polis_page_1.continue_button).to_be_disabled()


def test_all_polis_fields_filled_in_correctly(page):
    """Проверяем что в случае когда все поля заполнены корретными данными мы переходим на страницу оплаты.
        Входные данные:
        1. Сумма покрытия - дефолтное значение: 500.000
        2. Имя: Иванов Иван
        3. Дата рождения: относительная величина -240 месяцев от текущей даты.
        4. Паспорт: 1234-123123
        5. Дата выдачи: относительная величина -2 месяцев от текущей даты.
        6. Адрес: Спб
        7. Телефон: 1231213456
        8. почта:  john.doe@mail.ru
        9. Страхователь является застрахованным.
    Результат: должны получить сообщение 'К сожалению, оформление полиса онлайн невозможно.'

    """
    new_polis_page_1 = NewPolisStep1(page)
    new_polis_page_2 = NewPolisStep2(page)

    new_polis_page_1.check_no_virus_contact()
    new_polis_page_1.check_agreement()
    new_polis_page_1.click_continue()
    new_polis_page_1.verify_step_is_not_active()

    dob = datetime.datetime.today() - datetime.timedelta(weeks=4 * 240)
    dob_string = dob.strftime("%d%m%Y")
    issue_date = (datetime.datetime.today() - datetime.timedelta(weeks=4)).strftime("%d%m%Y")

    new_polis_page_2.fill_in_form(
        fio="Иванов Иван",
        dob=dob_string,
        passport="1234123123",
        issue_date=issue_date,
        address="Спб",
        phone="1231213456",
        email="john.doe@mail.ru"
    )

    new_polis_page_2.click_proceed_to_payment_button()

    expect(page.get_by_text("К сожалению, оформление полиса онлайн невозможно.")).to_be_visible(timeout=15000)


@pytest.mark.parametrize("missing_field", [
    {"field_name": "fio",
     "exp_error_message": "Не указана фамилия."},
    {"field_name": "dob",
     "exp_error_message": "Не указана дата рождения."},
    {"field_name": "passport",
     "exp_error_message": "Не указаны серия/номер паспорта."},
    {"field_name": "issue_date",
     "exp_error_message": "Не указаны дата выдачи паспорта."},
    {"field_name": "address",
     "exp_error_message": "Не указан адрес регистрации."},
    {"field_name": "phone",
     "exp_error_message": "Не указан номер телефона."},
    {"field_name": "email",
     "exp_error_message": "Не указан E-Mail."}
] #,ids=format_dictionary_test_id
)
def test_correct_error_shown_when_mandatory_field_missing(page, missing_field):
    new_polis_page_1 = NewPolisStep1(page)
    new_polis_page_2 = NewPolisStep2(page)

    new_polis_page_1.check_no_virus_contact()
    new_polis_page_1.check_agreement()
    new_polis_page_1.click_continue()
    new_polis_page_1.verify_step_is_not_active()

    fio = None if missing_field["field_name"] == "fio" else "Петров Петр"
    dob = None if missing_field["field_name"] == "dob" else (
        (datetime.datetime.today() - datetime.timedelta(weeks=4 * 240)).strftime("%d%m%Y"))
    passport = None if missing_field["field_name"] == "passport" else "1234123124"
    issue_date = None if missing_field["field_name"] == "issue_date" else (
        (datetime.datetime.today() - datetime.timedelta(weeks=4)).strftime("%d%m%Y"))
    address = None if missing_field["field_name"] == "address" else "Москва"
    phone = None if missing_field["field_name"] == "phone" else "9211234567"
    email = None if missing_field["field_name"] == "email" else "john.doe@gmail.com"

    new_polis_page_2.fill_in_form(
        fio=fio,
        dob=dob,
        passport=passport,
        issue_date=issue_date,
        address=address,
        phone=phone,
        email=email
    )
    new_polis_page_2.click_proceed_to_payment_button()

    errors = new_polis_page_2.get_errors(exp_count=1)
    assert missing_field["exp_error_message"] in errors


@pytest.mark.parametrize("age_input", [
    {"age": 17,
     "allowed": False},
    {"age": 18,
     "allowed": True},
    {"age": 19,
     "allowed": True},
    {"age": 54,
     "allowed": True},
    {"age": 55,
     "allowed": True},
    {"age": 56,
     "allowed": False},
],
                         ids=format_dictionary_test_id
                         )
def test_allowed_age_of_insurer_from_18_to_55(page, age_input):
    """Тест на то что страхователем может быть только человек в возрасте от 18 до 55"""
    new_polis_page_1 = NewPolisStep1(page)
    new_polis_page_2 = NewPolisStep2(page)

    new_polis_page_1.check_no_virus_contact()
    new_polis_page_1.check_agreement()
    new_polis_page_1.click_continue()
    new_polis_page_1.verify_step_is_not_active()

    today = datetime.datetime.today()
    year = today.year
    month = today.month
    day = today.day

    dob_year = year - age_input["age"]
    dob = f"{str(day).zfill(2)}{str(month).zfill(2)}{dob_year}"

    fio = "Петров Петр Петрович"
    passport = "1234123124"
    issue_date = (datetime.datetime.today() - datetime.timedelta(weeks=4)).strftime("%d%m%Y")
    address = "Москва"
    phone = "9211234567"
    email = "john.doe@gmail.com"

    new_polis_page_2.fill_in_form(
        fio=fio,
        dob=dob,
        passport=passport,
        issue_date=issue_date,
        address=address,
        phone=phone,
        email=email
    )
    new_polis_page_2.click_proceed_to_payment_button()

    if not age_input["allowed"]:
        errors = new_polis_page_2.get_errors(exp_count=1)
        assert """Возраст застрахованного должен быть не менее 18 и не более 55 лет""" in errors
    else:
        errors = new_polis_page_2.get_errors(exp_count=0)
        assert errors == []


@pytest.mark.parametrize("age_input", [
    {"age": 2,
     "allowed": False},
    {"age": 3,
     "allowed": True},
    {"age": 4,
     "allowed": True},
    {"age": 54,
     "allowed": True},
    {"age": 55,
     "allowed": True},
    {"age": 56,
     "allowed": False},
],
                         ids=format_dictionary_test_id
                         )
def test_allowed_age_of_insured_from_3_to_55(page, age_input):

    """Тест на то что застрахованным может быть только человек в возрасте от 3 до 55"""
    new_polis_page_1 = NewPolisStep1(page)
    new_polis_page_2 = NewPolisStep2(page)

    new_polis_page_1.check_no_virus_contact()
    new_polis_page_1.check_agreement()
    new_polis_page_1.click_continue()
    new_polis_page_1.verify_step_is_not_active()

    today = datetime.datetime.today()

    dob_year = today.year - age_input["age"]
    insured_dob = f"{str(today.day).zfill(2)}{str(today.month).zfill(2)}{dob_year}"

    fio = "Петров Петр Петрович"
    insurer_dob = (datetime.datetime.today() - datetime.timedelta(weeks=4 * 240)).strftime("%d%m%Y")
    passport = "1234123124"
    issue_date = (datetime.datetime.today() - datetime.timedelta(weeks=4)).strftime("%d%m%Y")
    address = "Москва"
    phone = "9211234567"
    email = "john.doe@gmail.com"

    insured_passport = "1234123124" if age_input["age"] in [54, 55, 56] else None # Кейс когда требуется паспорт
    insured_issue_date = (datetime.datetime.today() - datetime.timedelta(weeks=4)).strftime("%d%m%Y") \
        if age_input["age"] in [54, 55, 56] else None # Кейс когда требуется паспорт

    new_polis_page_2.fill_in_form(
        fio=fio,
        dob=insurer_dob,
        passport=passport,
        issue_date=issue_date,
        address=address,
        phone=phone,
        email=email,
        insured_name="Сидоров Егор Палыч",
        insured_dob=insured_dob,
        insured_passport=insured_passport,
        insured_issue_date=insured_issue_date
    )
    new_polis_page_2.click_proceed_to_payment_button()

    if not age_input["allowed"]:
        errors = new_polis_page_2.get_errors(exp_count=1)
        assert """Возраст застрахованного должен быть не менее 3 и не более 55 лет""" in errors
    else:
        errors = new_polis_page_2.get_errors(exp_count=0)
        assert errors == []
        expect(page.get_by_text("К сожалению, оформление полиса онлайн невозможно.")).to_be_visible(timeout=10000)
