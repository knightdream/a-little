using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace NewGame.Editor
{
    public static class PrototypeSetup
    {
        [MenuItem("New Game/Create Test Room")]
        public static void CreateTestRoom()
        {
            if (!Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            System.IO.Directory.CreateDirectory("Assets/Scenes");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            new GameObject("Game Bootstrap").AddComponent<GameBootstrap>();
            EditorSceneManager.SaveScene(scene, "Assets/Scenes/TestRoom.unity");
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene("Assets/Scenes/TestRoom.unity", true) };
            AssetDatabase.SaveAssets();
            Debug.Log("NEWGAME_SETUP_OK: TestRoom created and scripts compiled.");
        }
    }
}
