"""Unit tests for repositories."""

import pytest


class TestMovieRepository:
    """Tests for MovieRepository."""

    @pytest.mark.asyncio
    async def test_get_by_code_not_found(self, uow):
        """Test getting non-existent movie."""
        found = await uow.movies.get_by_code(99999)
        assert found is None

    @pytest.mark.asyncio
    async def test_get_total_count(self, uow):
        """Test getting total movie count."""
        count = await uow.movies.get_total_count()
        assert count >= 0


class TestUserRepository:
    """Tests for UserRepository."""

    @pytest.mark.asyncio
    async def test_get_or_create_new_user(self, uow):
        """Test creating new user via get_or_create."""
        user, created = await uow.users.get_or_create(
            telegram_id=123456789,
            username="testuser",
            full_name="Test User",
        )
        await uow.commit()

        assert created is True
        assert user.telegram_id == 123456789
        assert user.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_or_create_existing_user(self, uow):
        """Test getting existing user via get_or_create."""
        await uow.users.get_or_create(
            telegram_id=987654321,
            username="existing",
            full_name="Existing User",
        )
        await uow.commit()

        user, created = await uow.users.get_or_create(
            telegram_id=987654321,
            username="existing",
            full_name="Existing User",
        )

        assert created is False
        assert user.telegram_id == 987654321

    @pytest.mark.asyncio
    async def test_get_total_count(self, uow):
        """Test getting total user count."""
        await uow.users.get_or_create(telegram_id=1, username="u1", full_name="U1")
        await uow.users.get_or_create(telegram_id=2, username="u2", full_name="U2")
        await uow.commit()

        count = await uow.users.get_total_count()
        assert count >= 2


class TestAdminRepository:
    """Tests for AdminRepository."""

    @pytest.mark.asyncio
    async def test_create_admin(self, uow):
        """Test creating admin."""
        await uow.admins.create_admin(
            telegram_id=111222333,
            username="admin_test",
            is_super=False,
        )
        await uow.commit()

        admin = await uow.admins.get_by_telegram_id(111222333)
        assert admin is not None
        assert admin.is_super_admin is False

    @pytest.mark.asyncio
    async def test_create_super_admin(self, uow):
        """Test creating super admin."""
        await uow.admins.create_admin(
            telegram_id=444555666,
            username="super_test",
            is_super=True,
        )
        await uow.commit()

        admin = await uow.admins.get_by_telegram_id(444555666)
        assert admin is not None
        assert admin.is_super_admin is True

    @pytest.mark.asyncio
    async def test_is_admin(self, uow):
        """Test checking admin status."""
        await uow.admins.create_admin(
            telegram_id=777888999,
            username="check_admin",
            is_super=False,
        )
        await uow.commit()

        is_admin = await uow.admins.is_admin(777888999)
        assert is_admin is True

        is_not_admin = await uow.admins.is_admin(111111111)
        assert is_not_admin is False
