"""Rating calculation domain service."""

from decimal import ROUND_HALF_UP, Decimal


class RatingCalculator:
    """Domain service for rating calculations."""

    @staticmethod
    def calculate_average(
        current_average: Decimal,
        current_count: int,
        new_score: int,
        old_score: int | None = None,
    ) -> tuple[Decimal, int]:
        """
        Calculate new average rating.

        Args:
            current_average: Current average rating
            current_count: Current number of ratings
            new_score: New rating score
            old_score: Previous score if updating existing rating

        Returns:
            Tuple of (new_average, new_count)
        """
        if old_score is not None:
            # Updating existing rating
            if current_count == 0:
                return Decimal(new_score), 1

            total = float(current_average) * current_count
            total = total - old_score + new_score
            new_average = Decimal(total / current_count).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            return new_average, current_count
        else:
            # New rating
            new_count = current_count + 1
            if current_count == 0:
                return Decimal(new_score), new_count

            total = float(current_average) * current_count + new_score
            new_average = Decimal(total / new_count).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            return new_average, new_count

    @staticmethod
    def calculate_from_scores(scores: list[int]) -> Decimal:
        """
        Calculate average from list of scores.

        Args:
            scores: List of rating scores

        Returns:
            Average rating as Decimal
        """
        if not scores:
            return Decimal("0.00")

        average = sum(scores) / len(scores)
        return Decimal(average).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def get_distribution(scores: list[int]) -> dict[int, int]:
        """
        Get rating distribution.

        Args:
            scores: List of rating scores

        Returns:
            Dict mapping score to count
        """
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for score in scores:
            if score in distribution:
                distribution[score] += 1
        return distribution
