import json
from datetime import datetime
from typing import Any, List

from pydantic import ValidationError, TypeAdapter

from src.models.alarm_model import AlarmStatus, AlarmModelToCreate, AlarmModel
from src.services.storage.interfaces import IAlarmsStoragehandler
from src.utils import statuses
from src.utils.exceptions.storage import StorageValidationError, StorageNotFound, UnexpectedResponse


class AlarmsStoragehandler(IAlarmsStoragehandler):
    async def get(self, _id: str) -> AlarmModel:
        """"""
        response = await self.request_handler.get(f"alarms/get_alarm/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                try:
                    return AlarmModel.model_validate_json(response.body)
                except ValidationError as err:
                    self.logger.error(f"StorageValidationError: {str(err)}")
                    raise StorageValidationError(str(err))
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found alarm with id: {_id}")
                raise StorageNotFound(f"Storage not found alarm with id: {_id}")
            case _:
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def get_all_by_parent(self, _id: str) -> list[AlarmModel]:
        """"""
        response = await self.request_handler.get(f"alarms/get_all_alarm_by_parent_id/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                ta = TypeAdapter(List[AlarmModel])  # Need to validate list of pydantic models
                try:
                    return ta.validate_json(response.body)
                except ValidationError as err:
                    self.logger.error(f"StorageValidationError: {str(err)}")
                    raise StorageValidationError(str(err))
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found alarms relates to entity with id: {_id}")
                raise StorageNotFound(f"Storage not found alarms relates to entity with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def get_all_by_user(self, _id: str) -> list[AlarmModel]:
        """"""
        response = await self.request_handler.get(f"alarms/get_all_user_alarms/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                ta = TypeAdapter(List[AlarmModel])  # Need to validate list of pydantic models
                try:
                    return ta.validate_json(response.body)
                except ValidationError as err:
                    self.logger.error(f"StorageValidationError: {str(err)}")
                    raise StorageValidationError(str(err))
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found alarms relates to user with id: {_id}")
                raise StorageNotFound(f"Storage not found alarms relates to user with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def get_all_ready(self) -> list[AlarmModel]:
        response = await self.request_handler.get("alarms/get_all_ready_alarms")

        match response.status:
            case statuses.SUCCESS_200:
                ta = TypeAdapter(List[AlarmModel])  # Need to validate list of pydantic models
                try:
                    return ta.validate_json(response.body)
                except ValidationError as err:
                    self.logger.error(f"StorageValidationError: {str(err)}")
                    raise StorageValidationError(str(err))
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found alarms with READY status")
                raise StorageNotFound(f"Storage not found alarms with READY status")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def create(self, alarm: AlarmModelToCreate, next_notion_time: datetime, repeat_interval: int) -> str:
        """
        :param alarm:
        :param next_notion_time:
        :param repeat_interval:
        :return:
        """
        response = await self.request_handler.post(
            f"alarms/create_alarm?next_notion_time={next_notion_time}&repeat_interval={repeat_interval}",
            body=alarm.model_dump()
        )

        match response.status:
            case statuses.CREATED_201:
                self.logger.info(f"Alarm was successful created with id: {response.body}")
                return response.body
            case statuses.VALIDATION_ERROR_422:
                self.logger.error(f"Request body doesn't match validation: {response.body}")
                raise StorageValidationError(f"Request body doesn't match validation: {response.body}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def postpone_repeatable(self, _id: str) -> datetime:
        """"""
        response = await self.request_handler.patch(f"alarms/postpone_repeatable_alarm/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                try:
                    body: dict = json.loads(response.body)
                    next_notion_time: str = body["next_notion_time"]
                    result = datetime.strptime(
                        next_notion_time.split(".")[0],
                        "%Y-%m-%d %H:%M:%S"
                    )
                    self.logger.info(f"Successful postpone alarm with id {_id}. New notion time: {result}")
                    return result
                except KeyError:
                    self.logger.error(f"UnexpectedResponse: No 'next_notion_time' key in response {response.body}")
                    raise UnexpectedResponse(f"No 'next_notion_time' key in response {response.body}")
                except ValueError:
                    self.logger.error(f"UnexpectedResponse: Can't parse dateTime from response: {response.body}")
                    raise UnexpectedResponse(f"Can't parse dateTime from response: {response.body}")
            case statuses.BAD_REQUEST_400:
                self.logger.error(f"Bad Request: {response.body}")
                raise StorageValidationError(f"Bad Request: {response.body}")
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found alarm with id: {_id}")
                raise StorageNotFound(f"Storage not found alarm with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def path(self, _id: str, new_data: dict[str, Any]) -> None:
        response = await self.request_handler.patch(f"alarms/update_alarm/{_id}", body=new_data)

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info("Alarm was successful updated")
                return
            case statuses.VALIDATION_ERROR_422:
                self.logger.error(f"Request body doesn't match validation: {response.body}")
                raise StorageValidationError(f"Request body doesn't match validation: {response.body}")
            case statuses.BAD_REQUEST_400:
                self.logger.error(f"{response.body} with id: {_id}")
                raise StorageValidationError(f"{response.body} with id: {_id}")
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found alarm with id: {_id}")
                raise StorageNotFound(f"Storage not found alarm with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def update_status(self, _id: str, new_status: AlarmStatus) -> None:

        response = await self.request_handler.patch(f"alarms/update_alarm_status/{_id}?new_status={new_status}")

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info("Alarm was successful updated")
                return
            case statuses.VALIDATION_ERROR_422:
                self.logger.error(f"Request body doesn't match validation: {response.body}")
                raise StorageValidationError(f"Request body doesn't match validation: {response.body}")
            case statuses.BAD_REQUEST_400:
                self.logger.error(f"{response.body} with id: {_id}")
                raise StorageValidationError(f"{response.body} with id: {_id}")
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found theme with id: {_id}")
                raise StorageNotFound(f"Storage not found theme with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def delete(self, _id: str) -> None:

        response = await self.request_handler.delete(f"alarms/delete_alarm_by_id/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info("Alarm was successful delete")
                return
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found alarm with id: {_id}")
                raise StorageNotFound(f"Storage not found alarm with id: {_id}")
            case statuses.BAD_REQUEST_400:
                self.logger.error(f"{response.body} with id: {_id}")
                raise StorageValidationError(f"{response.body} with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def delete_by_parent(self, _id: str) -> None:
        response = await self.request_handler.delete(f"alarms/delete_all_alarm_by_parent/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info(f"{response.body} alarm was successful deleted")
                return
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found alarm related to entity with id: {_id}")
                raise StorageNotFound(f"Storage not found alarm related to entity with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")

    async def delete_by_user(self, _id: str) -> None:
        response = await self.request_handler.delete(f"alarms/delete_all_user_alarms/{_id}")

        match response.status:
            case statuses.SUCCESS_200:
                self.logger.info(f"{response.body} alarm was successful deleted")
                return
            case statuses.NOT_FOUND_404:
                self.logger.info(f"Storage not found alarm related to user with id: {_id}")
                raise StorageNotFound(f"Storage not found alarm related to user with id: {_id}")
            case _:
                self.logger.error(f"Unacceptable response status code: {response.status}")
                raise UnexpectedResponse(f"Unacceptable response status code: {response.status}")
