using UnityEngine;

namespace NewGame
{
    // The prototype uses original placeholder shapes; no Cave Story assets are required.
    public static class Prototype
    {
        private static Sprite square;

        public static GameObject Box(string name, Vector2 position, Vector2 size, Color color)
        {
            if (square == null)
                square = Sprite.Create(Texture2D.whiteTexture, new Rect(0, 0, 1, 1), new Vector2(.5f, .5f), 1);
            var obj = new GameObject(name);
            obj.transform.position = position;
            obj.transform.localScale = size;
            obj.AddComponent<SpriteRenderer>().sprite = square;
            obj.GetComponent<SpriteRenderer>().color = color;
            return obj;
        }

        public static Rigidbody2D Body(GameObject obj, float gravity = 3)
        {
            var body = obj.AddComponent<Rigidbody2D>();
            body.gravityScale = gravity;
            body.freezeRotation = true;
            body.interpolation = RigidbodyInterpolation2D.Interpolate;
            body.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
            return body;
        }
    }
}
