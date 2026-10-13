using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace NewGame.Editor
{
    // Batch-only integration check: run the actual room and allow physics to settle.
    public static class PrototypeSmokeCheck
    {
        private static double deadline;
        private static bool checkedRoom;
        private static bool previousEnabled;
        private static EnterPlayModeOptions previousOptions;

        public static void Run()
        {
            EditorSceneManager.OpenScene("Assets/Scenes/TestRoom.unity");
            previousEnabled = EditorSettings.enterPlayModeOptionsEnabled;
            previousOptions = EditorSettings.enterPlayModeOptions;
            EditorSettings.enterPlayModeOptionsEnabled = true;
            EditorSettings.enterPlayModeOptions = EnterPlayModeOptions.DisableDomainReload;
            deadline = EditorApplication.timeSinceStartup + 60;
            Application.logMessageReceived += OnLog;
            EditorApplication.update += Tick;
            EditorApplication.isPlaying = true;
        }

        private static void OnLog(string message, string stack, LogType type)
        {
            if (type == LogType.Exception || type == LogType.Error || type == LogType.Assert)
                EditorApplication.Exit(1);
        }

        private static void Tick()
        {
            if (EditorApplication.timeSinceStartup > deadline) { EditorApplication.Exit(2); return; }
            if (!EditorApplication.isPlaying || Time.time < 3 || checkedRoom) return;
            checkedRoom = true;
            var hero = Object.FindFirstObjectByType<PlayerController>();
            var enemies = Object.FindObjectsByType<Walker>(FindObjectsSortMode.None);
            if (hero == null || enemies.Length != 3 || hero.transform.position.y < -1.1f)
                throw new System.Exception("Room spawn or floor collision failed.");
            hero.Hurt(1);
            hero.Hurt(1);
            if (hero.Health != 4) throw new System.Exception("Damage protection failed.");
            hero.AddExperience(1);
            if (hero.Experience != 1) throw new System.Exception("Experience counter failed.");
            Projectile.Fire(hero.transform.position + Vector3.right, 1);
            Debug.Log("NEWGAME_SMOKE_OK: room, player grounding, enemies, damage protection, XP, projectile spawn.");
            EditorSettings.enterPlayModeOptionsEnabled = previousEnabled;
            EditorSettings.enterPlayModeOptions = previousOptions;
            EditorApplication.Exit(0);
        }
    }
}
