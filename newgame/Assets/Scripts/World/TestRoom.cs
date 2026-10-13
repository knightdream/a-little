using UnityEngine;

namespace NewGame
{
    public static class TestRoom
    {
        public static void Build()
        {
            // Integer-grid level data. Replace this builder with Tilemap levels later.
            for (int x = -14; x <= 24; x++) Ground(x, -2);
            for (int y = -1; y <= 6; y++) { Ground(-14, y); Ground(24, y); }
            for (int x = -7; x <= -4; x++) Ground(x, 1);
            for (int x = 5; x <= 8; x++) Ground(x, 1);
            for (int x = 12; x <= 15; x++) Ground(x, 3);
        }

        private static void Ground(int x, int y)
        {
            var tile = Prototype.Box("Terrain", new Vector2(x, y), Vector2.one, new Color(.24f, .32f, .40f));
            tile.layer = 8;
            tile.AddComponent<BoxCollider2D>();
        }
    }
}
