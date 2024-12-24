import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from helpers.validation import extract_and_validate_url
from db_utils.db_handler import check_and_save_survey
from utils.texts import group_descriptions, message_example
from utils.variants import available_groups, available_event_styles, survey_steps, event_data_dict
from keyboards.inline_row import make_inline_keyboard
from aiogram.types import KeyboardButton
from main import bot

router = Router()
BOT_TOKEN = os.getenv("BOT_TOKEN")


class EventSurvey(StatesGroup):
    survey_finished_photo = State()
    update_edited_field = State()
    edit_field = State()
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
    if message.chat.id < 0:
        pass
    else:
        await message.answer(
            text="Вы вышли из анкеты!\nМожете начать заново, введите /start",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(Command("предыдущий_шаг"))
async def back_command(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
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
            await intermediate_function(message, state, 'callback_data_placeholder')
        elif current_state == "EventSurvey:contacts_inserted":
            await input_description(message, state)
        elif current_state == "EventSurvey:registration_url_inserted":
            await input_contacts(message, state)
        elif current_state == "EventSurvey:tags_inserted":
            await input_registration_url(message, state)


# Команда начала опроса
@router.message(Command("survey"))
async def cmd_choosing_group(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
        await state.set_state(EventSurvey.choosing_group)
        await message.answer(
            text="<b>Выберите группу для публикации ивента:</b>\n" + group_descriptions,
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
    if callback.message.chat.id < 0:
        pass
    else:
        if callback.message.text != "/предыдущий_шаг":
            await state.update_data(chosen_group=callback.data)
        await state.set_state(EventSurvey.offer_message_example)
        await callback.message.answer(
            message_example,
            reply_markup=ReplyKeyboardRemove()
        )
        await input_event_name(callback.message, state)


# Функция, которая запрашивает ввод имени события
async def input_event_name(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
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
    if message.chat.id < 0:
        pass
    else:
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
    if message.chat.id < 0:
        pass
    else:
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
    if callback.message.chat.id < 0:
        pass
    elif callback.data == 'онлайн':
        await state.update_data(event_style=callback.data)
        await state.update_data(event_location='')
        await input_description(callback.message, state)
    else:
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
    if message.chat.id < 0:
        pass
    else:
        if message.chat.id < 0:
            pass
        else:
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
    if message.chat.id < 0:
        pass
    else:
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
    if message.chat.id < 0:
        pass
    else:
        if message.text != "/предыдущий_шаг":
            await state.update_data(event_contacts=message.text)
        await state.set_state(EventSurvey.input_registration_url)
        await message.answer(
            text="<b>Введите ссылку для регистрации на мероприятие:</b>\nНапример, 'https://example.com/register'\n",
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
    if message.chat.id < 0:
        pass
    else:
        if extract_and_validate_url(message.text) is None:
            await message.answer(
                text=
                "К сожалению, предоставленная вами ссылка не валидна. "
                "Пожалуйста, убедитесь, что ссылка корректна. Например, она может выглядеть так: "
                "example.com или https://example.com."
            )
            await input_registration_url(message, state)
        else:
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
    if message.chat.id < 0:
        pass
    else:
        if message.text != "/предыдущий_шаг" and message.text != "Выберите поле, которое хотите отредактировать.\n\nДоступные варианты:":
            output_string = '\n' + ' '.join(
                f'#{word}' if not word.startswith('#') else word for word in message.text.split())
            await state.update_data(event_tags=output_string)
        await state.set_state(EventSurvey.survey_finished)
        data = await state.get_data()
        survey_text = ""
        survey_text += f"<b>{data['event_name']}</b>\n"
        survey_text += f"<b>{data['event_date']}</b>\n"
        survey_text += f"<b>Формат мероприятия: </b> {data['event_style']}\n"
        if data['event_location'] != 'Доступные варианты:':
            survey_text += f"<b>Местоположение: </b> {data['event_location']}\n"
        survey_text += f"{data['event_description']}\n"
        survey_text += f"<b>Контактная информация: </b> {data['event_contacts']}\n"
        survey_text += f"{data['event_tags']}\n"
        await state.update_data(survey_text=survey_text)
        await message.answer(
            text="<b>Ваш ивент:</b>\n" + survey_text,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Опубликовать ивент"),
                        KeyboardButton(text="Редактировать ивент"),
                        KeyboardButton(text="Добавить фото ивента"),
                        KeyboardButton(text="/Выход")
                    ]
                ],
                resize_keyboard=True,
            ),
        )


async def process_event_photo(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
        await message.answer(
            text="Вы можете добавить фото к карточке вашего мероприятия. Просто пришлите его мне."
        )

        await state.set_state(EventSurvey.survey_finished_photo)


@router.message(EventSurvey.survey_finished_photo)
async def post_message_with_photo(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
        data = await state.get_data()
        channel = data['chosen_group']
        survey_text = data['survey_text']
        chat_id_without_at = channel.replace("@", "")
        existing_message = check_and_save_survey(data)
        if existing_message:
            await message.answer(
                "Такой ивент уже есть! Создайте новый!",
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
                f"Ивент отправлен в чат: t.me/{chat_id_without_at}",
                reply_markup=ReplyKeyboardRemove()
            )

            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(
                text="Ссылка для регистрации", url=data['event_url']
            ))
            keyboard = builder.as_markup()
            photo = message.photo[-1]
            photo_file_id = photo.file_id

            await bot.send_photo(
                chat_id=channel,
                caption=survey_text,
                photo=photo_file_id,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            await message.answer(
                "Создайте еще один ивент!",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="/start"),
                        ]
                    ],
                    resize_keyboard=True,
                )
            )
@router.message(EventSurvey.survey_finished)
async def post_message(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
        if message.text == "Добавить фото ивента":
            await process_event_photo(message,state)
        else:
            if message.text == "Редактировать ивент":
                await edit_survey(message, state)
            else:
                data = await state.get_data()
                channel = data['chosen_group']
                survey_text = data['survey_text']
                chat_id_without_at = channel.replace("@", "")
                existing_message = check_and_save_survey(data)
                if existing_message:
                    await message.answer(
                        "Такой ивент уже есть! Создайте новый!",
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
                        f"Ивент отправлен в чат: t.me/{chat_id_without_at}",
                        reply_markup=ReplyKeyboardRemove()
                    )

                    builder = InlineKeyboardBuilder()
                    builder.row(InlineKeyboardButton(
                        text="Ссылка для регистрации", url=data['event_url']
                    ))
                    keyboard = builder.as_markup()
                    await bot.send_message(
                        chat_id=channel,
                        text=survey_text,
                        reply_markup=keyboard,
                        message_thread_id=None,
                        parse_mode="HTML"
                    )
                    await message.answer(
                        "Создайте еще один ивент!",
                        reply_markup=ReplyKeyboardMarkup(
                            keyboard=[
                                [
                                    KeyboardButton(text="/start"),
                                ]
                            ],
                            resize_keyboard=True,
                        )
                    )


async def edit_survey(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
        await message.answer(
            text="Выберите поле, которое хотите отредактировать.\n\nДоступные варианты:",
            reply_markup=make_inline_keyboard(survey_steps)
        )
        await state.set_state(EventSurvey.edit_field)


@router.callback_query(EventSurvey.edit_field)
async def edit_field(query: CallbackQuery, state: FSMContext) -> None:
    if query.message.chat.id < 0:
        pass
    else:
        if query.data == "Вернуться к анкете.":
            await state.set_state(EventSurvey.tags_inserted)
            await survey_finished(query.message, state)
        else:
            data = await state.get_data()
            if query.data in event_data_dict:
                editing_field_key = event_data_dict[query.data]
                current_value = data.get(editing_field_key)

                if current_value != "":
                    await query.message.answer(
                        text=f"Сейчас поле {query.data} выглядит так: {current_value}."
                    )
                else:
                    await query.message.answer(
                        text=f"Сейчас поле {query.data} не заполнено."
                    )

                await state.set_state(EventSurvey.update_edited_field)
                await state.update_data(editing_field_key=editing_field_key)
                await query.message.answer(
                    text="Заполните поле заново.",
                    reply_markup=ReplyKeyboardRemove()
                )
            else:
                await query.message.answer(text="Неизвестное поле для редактирования.")


@router.message(EventSurvey.update_edited_field)
async def update_edited_field(message: Message, state: FSMContext):
    if message.chat.id < 0:
        pass
    else:
        data = await state.get_data()
        editing_field_key = data.get('editing_field_key')

        await state.update_data(**{editing_field_key: message.text})

        await message.reply(
            text="Отлично, сохранил отредактированное поле."
        )

        await state.set_state(EventSurvey.tags_inserted)
        await edit_survey(message, state)


@router.message(F.text)
async def any_message_handler(message: Message, state: FSMContext) -> None:
    if message.chat.id < 0:
        pass
    else:
        current_state = await state.get_state()
        if current_state == "EventSurvey:choosing_group":
            await message.answer("Пожалуйста, используйте кнопки для ввода.", reply_markup=ReplyKeyboardRemove())
            await cmd_choosing_group(message, state)
        elif current_state == "EventSurvey:choosing_event_style":
            await message.answer("Пожалуйста, используйте кнопки для ввода.", reply_markup=ReplyKeyboardRemove())
            await choosing_event_style(message, state)
        else:
            await message.answer(
                "Я не знаю такой команды,\nнапишите /start"
            )