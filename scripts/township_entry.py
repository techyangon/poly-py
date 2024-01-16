import asyncio
import csv

from poly.config import Settings, get_settings
from poly.db import get_session
from poly.services.locations import (
    get_city_by_name,
    get_state_by_name,
    save_city,
    save_state,
    save_townships,
)


async def seed_data(settings: Settings):
    async_session = await get_session(settings=settings)

    with open(settings.townships_file, newline="") as csvfile:
        townships_csv = csv.reader(csvfile)

        state, city, townships = "", "", []
        for row in townships_csv:
            if state == "":
                await save_state(name=row[0], async_session=async_session)

                saved_state = await get_state_by_name(
                    name=row[0], async_session=async_session
                )
                if saved_state:
                    await save_city(
                        name=row[1],
                        state_id=saved_state.id,
                        async_session=async_session,
                    )

                state = row[0]
                city = row[1]
                townships.append(row[2])
            elif state == row[0]:
                if city != row[1]:
                    saved_city = await get_city_by_name(
                        name=city, async_session=async_session
                    )

                    if saved_city:
                        await save_townships(
                            townships=townships,
                            city_id=saved_city.id,
                            async_session=async_session,
                        )

                    saved_state = await get_state_by_name(
                        name=state, async_session=async_session
                    )
                    if saved_state:
                        await save_city(
                            name=row[1],
                            state_id=saved_state.id,
                            async_session=async_session,
                        )

                    city = row[1]
                    townships = []

                townships.append(row[2])
            else:
                # Save previous iteration data
                saved_city = await get_city_by_name(
                    name=city, async_session=async_session
                )

                if saved_city:
                    await save_townships(
                        townships=townships,
                        city_id=saved_city.id,
                        async_session=async_session,
                    )

                # Save current iteration data
                await save_state(name=row[0], async_session=async_session)

                saved_state = await get_state_by_name(
                    name=row[0], async_session=async_session
                )
                if saved_state:
                    await save_city(
                        name=row[1],
                        state_id=saved_state.id,
                        async_session=async_session,
                    )

                state = row[0]
                city = row[1]
                townships = []
                townships.append(row[2])

        saved_city = await get_city_by_name(name=city, async_session=async_session)

        if saved_city:
            await save_townships(
                townships=townships,
                city_id=saved_city.id,
                async_session=async_session,
            )


if __name__ == "__main__":
    settings = get_settings()

    asyncio.run(seed_data(settings=settings))
