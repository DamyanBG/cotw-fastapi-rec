from models.cat_models import CurrentRoundCatCreate
from queries.cat_queries import select_all_nr_cats, insert_current_round_cats, delete_all_nr_cats


async def round_end_logic():
    print("Job started")
    nr_cats = await select_all_nr_cats()
    current_round_cats = [
        CurrentRoundCatCreate(**cat.model_dump()) for cat in nr_cats
    ]
    await insert_current_round_cats(current_round_cats)
    await delete_all_nr_cats(nr_cats)
    print("Job done")
