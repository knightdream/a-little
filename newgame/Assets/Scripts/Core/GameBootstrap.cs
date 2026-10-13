using UnityEngine;

namespace NewGame
{
    public sealed class GameBootstrap : MonoBehaviour
    {
        private PlayerController player;
        private Camera view;

        private void Awake()
        {
            view = Camera.main;
            if (view == null)
            {
                var cameraObject = new GameObject("Main Camera");
                cameraObject.tag = "MainCamera";
                view = cameraObject.AddComponent<Camera>();
            }
            view.orthographic = true;
            view.orthographicSize = 6;
            view.backgroundColor = new Color(.06f, .09f, .16f);
            view.clearFlags = CameraClearFlags.SolidColor;
            TestRoom.Build();
            var hero = Prototype.Box("Player", new Vector2(-8, 0), new Vector2(.7f, 1.2f), Color.cyan);
            hero.AddComponent<BoxCollider2D>();
            Prototype.Body(hero);
            player = hero.AddComponent<PlayerController>();
            for (int i = 0; i < 3; i++)
                Walker.Spawn(new Vector2(0 + i * 6, 0));
        }

        private void LateUpdate()
        {
            if (player != null)
                view.transform.position = new Vector3(player.transform.position.x + 2, 1, -10);
        }

        private void OnGUI()
        {
            if (player == null) return;
            GUI.Box(new Rect(12, 12, 540, 80), "NEW GAME / Movement & combat prototype");
            GUI.Label(new Rect(24, 38, 520, 22), "A/D or arrows: move   Space: jump   J: shoot   R: restart");
            GUI.Label(new Rect(24, 60, 520, 22), $"Health: {player.Health} / 5     Weapon XP: {player.Experience}");
        }
    }
}
