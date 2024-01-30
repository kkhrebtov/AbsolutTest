from typing import List

import allure
from playwright.sync_api import expect


class NewPolisStep2:

    def __init__(self, page):
        self.page = page

    @property
    def _form_title(self):
        return self.page.locator(".calc-steps .step-2-title")

    @property
    def first_name_input(self):
        return self.page.locator("input[name='firstName']")

    @property
    def last_name_input(self):
        return self.page.locator("input[name='lastName']")

    @property
    def fio_input(self):
        return self.page.locator("#name")

    @property
    def dob_input(self):
        return self.page.locator("#dateBirth")

    @property
    def passport_id(self):
        return self.page.locator("#id")

    @property
    def issue_date(self):
        return self.page.locator("#idDate")

    @property
    def address(self):
        return self.page.locator("#address")

    @property
    def phone(self):
        return self.page.locator("#phone")

    @property
    def email(self):
        return self.page.locator("#email")

    @property
    def _is_same_person(self):
        return self.page.locator("input[name='addPerson']").locator("xpath=..").locator(".checkmark")

    @property
    def insured_name(self):
        return self.page.locator("#nameInsured")

    @property
    def insured_dob(self):
        return self.page.locator("#dateBirthInsured")

    @property
    def insured_passport(self):
        return self.page.locator("#idInsured")

    @property
    def insured_issue_date(self):
        return self.page.locator("#idDateInsured")

    @property
    def _proceed_to_payment_button(self):
        return self.page.locator("button:has-text('Перейти к оплате')")

    @property
    def calculator_form(self):
        return self.page.locator(".calc-col-content")

    def get_errors(self, exp_count: int = 0) -> List[str]:
        self.page.wait_for_load_state()
        expect(self.page.locator(".error")).to_have_count(exp_count)
        return self.page.locator(".error").all_inner_texts() if exp_count > 0 else []

    def check_step_is_active(self):
        with allure.step("Проверка статуса текущего шага: Current"):
            expect(self._form_title).to_have_attribute("class", "step-2-title current")

    def fill_in_form(self, fio: str = None, dob: str = None, passport: str = None,
                     issue_date: str = None, address: str = None, phone: str = None, email: str = None,
                     insured_name: str = None, insured_dob: str = None, insured_passport: str = None,
                     insured_issue_date: str = None):

        with allure.step("Заполнить данные страхователя: "):
            with allure.step(f"Вводим ФИО: {fio}"):
                if fio is not None:
                    self.fio_input.first.press_sequentially(fio)
            # with allure.step(f"Вводим Фамилию: {first_name}"):
            #     if first_name is not None:
            #         self.first_name_input.first.press_sequentially(first_name)
            # with allure.step(f"Вводим Имя: {last_name}"):
            #     if last_name is not None:
            #         self.last_name_input.first.press_sequentially(last_name)
            with allure.step(f"Вводим дату рождения: {dob}"):
                if dob is not None:
                    self.dob_input.press_sequentially(dob)
                    self.page.locator(".datepicker-years").press("Enter")
            with allure.step(f"Вводим паспорт: {passport}"):
                if passport is not None:
                    self.passport_id.press_sequentially(passport)
            with allure.step(f"Вводим дату выпуска: {issue_date}"):
                if issue_date is not None:
                    self.issue_date.press_sequentially(issue_date)
                    self.issue_date.press("Enter")
            with allure.step(f"Вводим адрес: {address}"):
                if address is not None:
                    self.address.press_sequentially(address)
            with allure.step(f"Вводим телефон: {phone}"):
                if phone is not None:
                    self.phone.click()
                    expect(self.phone).to_be_editable()
                    self.phone.press_sequentially(phone, delay=200)
                    self.phone.press("Enter")
            with allure.step(f"Вводим почту: {email}"):
                if email is not None:
                    self.email.press_sequentially(email)
                    self.email.press("Enter")
            if insured_name is not None:
                self._is_same_person.uncheck()
                expect(self._is_same_person).not_to_be_checked()
                with allure.step(f"Вводим имя застрахованного: {insured_name}"):
                    if insured_name is not None:
                        self.insured_name.press_sequentially(insured_name)
                with allure.step(f"Вводим дату рождения застрахованного: {insured_dob}"):
                    if insured_dob is not None:
                        self.insured_dob.press_sequentially(insured_dob)
                        self.insured_dob.press("Enter")
                with allure.step(f"Вводим паспорт застрахованного: {insured_passport}"):
                    if insured_passport is not None:
                        self.insured_passport.press_sequentially(insured_passport)
                with allure.step(f"Вводим дату выпуска паспорта застрахованного: {insured_issue_date}"):
                    if insured_issue_date is not None:
                        self.insured_issue_date.press_sequentially(insured_issue_date)
                        self.insured_issue_date.press("Enter")

    def click_proceed_to_payment_button(self):
        with allure.step("Нажать на кнопку 'Перейти к оплате'"):
            self._proceed_to_payment_button.click()