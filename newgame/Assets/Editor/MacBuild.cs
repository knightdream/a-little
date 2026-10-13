using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace NewGame.Editor
{
    public static class MacBuild
    {
        [MenuItem("New Game/Build Windowed Mac App")]
        public static void Build()
        {
            PlayerSettings.productName = "A Little";
            PlayerSettings.companyName = "KnightDream";
            PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Standalone, "com.knightdream.alittle");
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.defaultScreenWidth = 1100;
            PlayerSettings.defaultScreenHeight = 700;
            PlayerSettings.resizableWindow = true;
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { "Assets/Scenes/TestRoom.unity" },
                locationPathName = "Builds/macOS/A Little.app",
                target = BuildTarget.StandaloneOSX,
                options = BuildOptions.Development
            });
            if (report.summary.result != BuildResult.Succeeded)
                throw new System.Exception("Mac build failed: " + report.summary.result);
            Debug.Log("NEWGAME_MAC_BUILD_OK");
        }
    }
}
