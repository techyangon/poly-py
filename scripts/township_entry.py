import asyncio
import csv

from poly.config import Settings, get_settings
from poly.db import get_session
from poly.services.locations import save_city, save_state_and_city, save_townships


async def seed_data(settings: Settings):
    async_session = await get_session(settings=settings)

    with open(settings.townships_file, newline="") as csvfile:
        townships_csv = csv.reader(csvfile)

        state, city, townships = "", "", []
        for row in townships_csv:
            if state == "":
                state, city = row[0], row[1]
                await save_state_and_city(
                    city=city, state=state, async_session=async_session
                )

                townships.append(row[2])
            elif state == row[0]:
                if city != row[1]:
                    # {city} & {townships} holds data from previous iteration
                    await save_townships(
                        city=city, townships=townships, async_session=async_session
                    )

                    # Assign and save current iteration data
                    city = row[1]
                    await save_city(name=city, state=state, async_session=async_session)

                    townships = []
                townships.append(row[2])
            else:
                # {city} & {townships} holds data from previous iteration
                await save_townships(
                    city=city, townships=townships, async_session=async_session
                )

                # Save current iteration data
                state, city = row[0], row[1]
                await save_state_and_city(
                    city=city, state=state, async_session=async_session
                )

                townships = []
                townships.append(row[2])

        # Above iteration will skip last group of townships
        await save_townships(
            city=city, townships=townships, async_session=async_session
        )


if __name__ == "__main__":
    settings = get_settings()

    asyncio.run(seed_data(settings=settings))
