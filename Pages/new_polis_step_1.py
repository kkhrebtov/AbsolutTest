from enum import Enum

import allure
from playwright.sync_api import expect


class PolisAmount(Enum):
    POLIS_500_000 = "500 000 ₽"
    POLIS_100_000 = "100 000 ₽"


class NewPolisStep1:

    def __init__(self, page):
        self.page = page

    def select_polis_amount(self, amount: PolisAmount):
        with (allure.step("Выбор страховой суммы полиса")):
            self.page.locator("#options-checkbox").locator("xpath=..").locator(f"label").filter(
                has_text=amount.value).click(force=True)

    @property
    def _form_title(self):
        return self.page.locator(".calc-steps .step-1-title")

    @property
    def _is_medic_checkbox(self):
        return self.page.locator("input[name='medicine']").locator("xpath=..").locator(".checkmark")

    @property
    def _is_virus_contact_checkbox(self):
        return self.page.locator("input[name='virus-contact']").locator("xpath=..").locator(".checkmark")

    @property
    def _agreement_checkbox(self):
        return self.page.locator("input[name='agree-polis']").locator("xpath=..").locator(".checkmark")

    @property
    def continue_button(self):
        return self.page.locator("button[type='submit']")

    @property
    def medicine_info(self):
        return self.page.locator(".medicine-info")

    def verify_step_is_active(self):
        with allure.step("Проверка статуса текущего шага: Current"):
            expect(self._form_title).to_have_attribute("class", "step-1-title current")

    def verify_step_is_not_active(self):
        with allure.step("Проверка статуса текущего шага: Not current"):
            expect(self._form_title).not_to_have_attribute("class", "step-1-title current")

    def check_is_medic(self):
        with allure.step("Выбрать чекбокс: Профессиональная сфера связана с медицинской деятельностью"):
            if not self._is_medic_checkbox.is_checked():
                self._is_medic_checkbox.check()
                expect(self._is_medic_checkbox).to_be_checked()

    def uncheck_is_medic(self):
        with allure.step("Очистить чекбокс: Профессиональная сфера связана с медицинской деятельностью"):
            if self._is_medic_checkbox.is_checked():
                self._is_medic_checkbox.uncheck()
                expect(self._is_medic_checkbox).not_to_be_checked()

    def check_no_virus_contact(self):
        with allure.step("Выбрать чекбокс: отсутствуют лица с COVID-2019"):
            if not self._is_virus_contact_checkbox.is_checked():
                self._is_virus_contact_checkbox.check()
                expect(self._is_virus_contact_checkbox).to_be_checked()

    def uncheck_virus_contact(self):
        with allure.step("Очистить чекбокс: тсутствуют лица с COVID-2019"):
            if self._is_virus_contact_checkbox.is_checked():
                self._is_virus_contact_checkbox.uncheck()
                expect(self._is_virus_contact_checkbox).not_to_be_checked()

    def check_agreement(self):
        with allure.step("Выбрать чекбокс: Согласине на обработку персональных данных"):
            if not self._agreement_checkbox.is_checked():
                self._agreement_checkbox.check()
                expect(self._agreement_checkbox).to_be_checked()

    def uncheck_agreement(self):
        with allure.step("Очистить чекбокс: Согласине на обработку персональных данных"):
            if self._agreement_checkbox.is_checked():
                self._agreement_checkbox.uncheck()
                expect(self._agreement_checkbox).not_to_be_checked()

    def click_continue(self):
        with allure.step("Нажать на кнопку: Продолжить"):
            self.continue_button.click()

    def validate_polis_cost(self, exp_cost):
        expect(self.page.locator(".option-description:visible").locator("#price")).to_have_attribute("placeholder",
                                                                                                     exp_cost)

    def validate_polis_start_date(self, exp_start_date):
        expect(self.page.locator("input#dateStart.form-control").first).to_have_attribute("placeholder", exp_start_date)

    def validate_polis_end_date(self, exp_end_date):
        expect(self.page.locator("input#dateEnd.form-control").first).to_have_attribute("placeholder", exp_end_date)

