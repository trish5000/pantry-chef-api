from copy import deepcopy
from typing import List
from sqlalchemy.orm import Session

import app.food_item.model as food_item_model
import app.household.model as household_model
import app.recipe.schema as recipe_schema
import app.recipe.model as recipe_model


class recipe:
    @staticmethod
    def get_suggestions(db: Session, user_id: int):
        # TODO use Crud methods instead?
        recipes: List[recipe_model.Recipe] = (
            db.query(recipe_model.Recipe)
            .filter(recipe_model.Recipe.user_id == user_id)
            .all()
        )

        pantry: List[food_item_model.FoodItem] = (
            db.query(food_item_model.FoodItem)
            .filter(food_item_model.FoodItem.user_id == user_id)
            .all()
        )

        household_member: household_model.HouseholdMember = (
            db.query(household_model.HouseholdMember)
            .filter(household_model.HouseholdMember.user_id == user_id)
            .first()
        )

        num_to_serve: int = (
            db.query(household_model.HouseholdMember)
            .filter(
                household_model.HouseholdMember.head_of_household_id
                == household_member.head_of_household_id
            )
            .count()
        )
        suggestions: List[recipe_schema.RecipeSuggestion] = []

        for rcp in recipes:
            factor = num_to_serve / rcp.servings if rcp.servings < num_to_serve else 1.0

            missing_ingredients: List[recipe_model.Ingredient] = deepcopy(
                rcp.ingredients
            )
            for ingredient in missing_ingredients:
                ingredient.quantity = ingredient.quantity * factor

            for item in pantry:
                for ingredient in missing_ingredients:
                    if item.name.lower() == ingredient.name.lower():
                        if item.quantity >= ingredient.quantity:
                            missing_ingredients.remove(ingredient)
                        else:
                            ingredient.quantity = ingredient.quantity - item.quantity
                        break

            suggestion = recipe_schema.RecipeSuggestion(
                recipe=rcp,
                missing_ingredients=missing_ingredients,
            )
            suggestions.append(suggestion)

            suggestions.sort(key=lambda x: len(x.missing_ingredients))

        return suggestions
