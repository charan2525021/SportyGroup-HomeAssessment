"""Single match card: teams, metadata, and the odds grid."""

from selenium.webdriver.common.by import By

from controller.odds_grid import MatchResult, OddsGrid
from lib.base_control import BaseControl


class Match(BaseControl):
    """A single match card in the upcoming-matches list."""

    badge = (By.CSS_SELECTOR, ".matchMeta .badge")
    leagueName = (By.CSS_SELECTOR, ".matchMeta span:nth-child(2)")
    date = (By.CSS_SELECTOR, ".matchMeta span:nth-child(4)")
    home_team_name = (By.CSS_SELECTOR, ".teams div:nth-child(1) .teamName")
    away_team_name = (By.CSS_SELECTOR, ".teams div:nth-child(2) .teamName")

    def metaData(self):
        """Badge (UPCOMING / PAST), league, and kickoff date shown on the card."""
        return {
            "badge": self.get_text(self.badge),
            "leagueName": self.get_text(self.leagueName),
            "date": self.get_text(self.date)
        }

    def participants(self):
        """Home and away team names."""
        return {
            "home": self.get_text(self.home_team_name),
            "away": self.get_text(self.away_team_name),
        }

    def option(self):
        """Odds grid nested inside this match card."""
        return OddsGrid(self.driver, parent=self.parent.find_element(By.CSS_SELECTOR, ".oddsGrid"))

    def select_outcome(self):
        """Snapshot of the currently selected odds button on this card."""
        return {
            "metadata": self.metaData(),
            "participants": self.participants(),
            "odds": self.get_text((By.CSS_SELECTOR, ".oddsButtonSelected .oddsButtonValue")),
            "selection": self.get_text((By.CSS_SELECTOR, ".oddsButtonSelected .oddsButtonLabel")),
        }
