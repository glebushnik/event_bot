import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup

from db_utils.db_handler import check_and_save_survey
from utils.texts import group_descriptions, message_example
from utils.variants import available_groups, available_event_styles
from keyboards.inline_row import make_inline_keyboard
import requests
from aiogram.types import KeyboardButton

router = Router()
BOT_TOKEN = os.getenv("BOT_TOKEN")

class EventSurvey(StatesGroup):
    survey_finished = State()
    tags_inserted = State()
    input_tags = State()
    registration_url_inserted = State()
    input_registration_url = State()
    contacts_inserted = State()
    input_contacts = State()
    location_inserted = State()
    input_location = State()
    description_inserted = State()
    input_description = State()
    choosing_event_style = State()
    date_time_inserted = State()
    input_date_time = State()
    event_name_inserted = State()
    input_event_name = State()
    message_example_shown = State()
    offer_message_example = State()
    choosing_group = State()


async def intermediate_function(message: Message, state: FSMContext, callback_data: str) -> None:
    user = message.from_user

    callback_query = CallbackQuery(
        id='dummy_id',
        from_user=user,
        chat_instance='dummy_chat_instance',
        message=message,
        data=callback_data,
    )

    await input_location(callback_query, state)

@router.message(Command("Выход"))
async def exit_command(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="Вы вышли из анкеты!\nМожете начать заново, введите /start"
    )


@router.message(Command("предыдущий_шаг"))
async def back_command(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == "EventSurvey:event_name_inserted":
        await cmd_choosing_group(message, state)
    elif current_state == "EventSurvey:date_time_inserted":
        await input_event_name(message, state)
    elif current_state == "EventSurvey:choosing_event_style":
        await input_date_time(message, state)
    elif current_state == "EventSurvey:location_inserted":
        await choosing_event_style(message, state)
    elif current_state == "EventSurvey:description_inserted":
        # Вызов промежуточной функции вместо input_location напрямую
        await intermediate_function(message, state, 'callback_data_placeholder')  # Укажите нужные данные
    elif current_state == "EventSurvey:contacts_inserted":
        await input_description(message, state)
    elif current_state == "EventSurvey:registration_url_inserted":
        await input_contacts(message, state)
    elif current_state == "EventSurvey:tags_inserted":
        await input_registration_url(message, state)

# Команда начала опроса
@router.message(Command("survey"))
async def cmd_choosing_group(message: Message, state: FSMContext) -> None:
    await state.set_state(EventSurvey.choosing_group)
    await message.answer(
        text="Выберите группу для публикации ивента:\n" + group_descriptions,
        reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/Выход")
                        ]
                    ],
                    resize_keyboard=True,
                ),
    )
    await message.answer(
        text="Доступные варианты:\n\n",
        reply_markup=make_inline_keyboard(available_groups),
    )


# Обработчик выбора группы
@router.callback_query(F.data.in_(available_groups))
async def offer_message_example(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message.text != "/предыдущий_шаг":
        await state.update_data(chosen_group=callback.data)
    await state.set_state(EventSurvey.offer_message_example)
    await callback.message.answer(
         message_example,
         reply_markup= ReplyKeyboardRemove()
    )
    await input_event_name(callback.message, state)


# Функция, которая запрашивает ввод имени события
async def input_event_name(message: Message, state: FSMContext) -> None:
    await state.set_state(EventSurvey.input_event_name)
    await message.answer(
        "\nХорошо, приступим к заполнению анкеты\n\n"
    )
    await message.answer(
        text="<b>Введите название события:</b>\nНапример, 'Вебинар по цифровому маркетингу'\n",
        reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/предыдущий_шаг"),
                            KeyboardButton(text="/Выход")
                        ]
                    ],
                    resize_keyboard=True,
                ),
    )
    await state.set_state(EventSurvey.event_name_inserted)



@router.message(EventSurvey.event_name_inserted)
async def input_date_time(message: Message, state: FSMContext) -> None:
    if message.text != "/предыдущий_шаг":
        await state.update_data(event_name=message.text)
    await state.set_state(EventSurvey.input_date_time)
    await message.answer(
        text="<b>Хорошо, введите дату проведения события:</b>\nНапример, '25 октября 2024 года, 15:00 - 17:00'\n",
        reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/предыдущий_шаг"),
                            KeyboardButton(text="/Выход")
                        ]
                    ],
                    resize_keyboard=True,
                ),
    )
    await state.set_state(EventSurvey.date_time_inserted)


@router.message(EventSurvey.date_time_inserted)
async def choosing_event_style(message: Message, state: FSMContext) -> None:
    if message.text != "/предыдущий_шаг":
        await state.update_data(event_date=message.text)
    await state.set_state(EventSurvey.choosing_event_style)
    await message.answer(
        text="<b>Теперь выберите вариант проведения мероприятия:</b>\n",
        reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/предыдущий_шаг"),
                            KeyboardButton(text="/Выход")
                        ]
                    ],
                    resize_keyboard=True,
                ),
    )
    await message.answer(
        text="<b>Доступные варианты:</b>\n\n",
        reply_markup=make_inline_keyboard(available_event_styles),
    )


@router.callback_query(F.data.in_(available_event_styles))
async def input_location(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message.text != "/предыдущий_шаг":
        await state.update_data(event_style=callback.data)
    await state.set_state(EventSurvey.input_location)
    await callback.message.answer(
        text="<b>Хорошо, введите местоположение события:</b>\nZoom (ссылка для подключения будет отправлена на email)",
        reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/предыдущий_шаг"),
                            KeyboardButton(text="/Выход")
                        ]
                    ],
                    resize_keyboard=True,
                ),
    )
    await state.set_state(EventSurvey.location_inserted)


@router.message(EventSurvey.location_inserted)
async def input_description(message: Message, state: FSMContext) -> None:
    if message.text != "/предыдущий_шаг":
        await state.update_data(event_location=message.text)
    await state.set_state(EventSurvey.input_description)
    await message.answer(
        text='<b>Следующий шаг - введите описание события:</b>\nНа этом вебинаре вы узнаете о современных стратегиях '
             'цифрового маркетинга'
             '\nи получите практические советы от экспертов отрасли.\n',
        reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/предыдущий_шаг"),
                            KeyboardButton(text="/Выход")
                        ]
                    ],
                    resize_keyboard=True,
                ),
    )
    await state.set_state(EventSurvey.description_inserted)


@router.message(EventSurvey.description_inserted)
async def input_contacts(message: Message, state: FSMContext) -> None:
    if message.text != "/предыдущий_шаг":
        await state.update_data(event_description=message.text)
    await state.set_state(EventSurvey.input_contacts)
    await message.answer(
        text="<b>Теперь введите свои контакты:</b>\nНапример, Иван Иванов @ivanivanov\n",
        reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/предыдущий_шаг"),
                            KeyboardButton(text="/Выход")
                        ]
                    ],
                    resize_keyboard=True,
                ),
    )
    await state.set_state(EventSurvey.contacts_inserted)


@router.message(EventSurvey.contacts_inserted)
async def input_registration_url(message: Message, state: FSMContext) -> None:
    if message.text != "/предыдущий_шаг":
        await state.update_data(event_contacts=message.text)
    await state.set_state(EventSurvey.input_registration_url)
    await message.answer(
        text="<b>Введите ссылку для регистрации на мероприятие:</b>Например, 'https://example.com/register'\n",
        reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/предыдущий_шаг"),
                            KeyboardButton(text="/Выход")
                        ]
                    ],
                    resize_keyboard=True,
                ),
    )
    await state.set_state(EventSurvey.registration_url_inserted)


@router.message(EventSurvey.registration_url_inserted)
async def input_tags(message: Message, state: FSMContext) -> None:
    if message.text != "/предыдущий_шаг":
        await state.update_data(event_url=message.text)
    await state.set_state(EventSurvey.input_tags)
    await message.answer(
        text="<b>Почти закончили! Введите теги:</b>\nНапример, маркетинг, вебинар, цифровые технологии, обучение\n",
        reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/предыдущий_шаг"),
                            KeyboardButton(text="/Выход")
                        ]
                    ],
                    resize_keyboard=True,
                ),
    )
    await state.set_state(EventSurvey.tags_inserted)

@router.message(EventSurvey.tags_inserted)
async def survey_finished(message: Message, state: FSMContext) -> None:
    if message.text != "/предыдущий_шаг":
        await state.update_data(event_tags=message.text)
    await state.set_state(EventSurvey.survey_finished)
    data = await state.get_data()
    survey_text = ""
    survey_text += f"<b>Название мероприятия: </b> {data['event_name']}\n"
    survey_text += f"<b>Дата и время: </b> {data['event_date']}\n"
    survey_text += f"<b>Формат мероприятия: </b> {data['event_style']}\n"
    survey_text += f"<b>Местоположение: </b> {data['event_location']}\n"
    survey_text += f"<b>Описание: </b> {data['event_description']}\n"
    survey_text += f"<b>Контактная информация: </b> {data['event_contacts']}\n"
    survey_text += f"<b>Ссылка на регистрацию: </b> {data['event_url']}\n"
    survey_text += f"<b>Ключевые слова(теги): </b> {data['event_tags']}\n"
    await state.update_data(survey_text=survey_text)
    await message.answer(
        text="<b>Ваша анкета:</b>\n" + survey_text,
        reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Опубликовать анкету"),
                            KeyboardButton(text="/Выход")
                        ]
                    ],
                    resize_keyboard=True,
                ),
    )


@router.message(EventSurvey.survey_finished)
async def post_message(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    channel = data['chosen_group']
    survey_text = data['survey_text']
    chat_id_without_at = channel.replace("@", "")
    existing_message = check_and_save_survey(data)
    if existing_message:
        await message.answer(
            "Такая анкета уже есть! Заполните ее заново",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="/start"),
                    ]
                ],
                resize_keyboard=True,
            )
        )
    else:
        await message.answer(
            f"Анкета отправлена в чат: t.me/{chat_id_without_at}",
            reply_markup=ReplyKeyboardRemove()
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": channel,
            "text": survey_text,
            "message_thread_id": None,
            "parse_mode": "HTML"
        }

        response = requests.post(url, data=data)

        await message.answer(
            "Заполните еще одну анкету!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="/start"),
                    ]
                ],
                resize_keyboard=True,
            )
        )


@router.message(F.text)
async def any_message_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == "EventSurvey:choosing_group":
        await message.answer("Пожалуйста, используйте кнопки для ввода.", reply_markup=ReplyKeyboardRemove())
        await cmd_choosing_group(message,state)
    elif current_state == "EventSurvey:choosing_event_style":
        await message.answer("Пожалуйста, используйте кнопки для ввода.", reply_markup=ReplyKeyboardRemove())
        await choosing_event_style(message,state)
    else:
        await message.answer(
            "Я не знаю такой команды,\nнапишите /start"
        )