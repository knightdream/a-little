using UnityEngine;

namespace NewGame
{
    public sealed class Projectile : MonoBehaviour
    {
        private bool spent;
        public static void Fire(Vector2 position, float direction)
        {
            var obj = Prototype.Box("Shot", position, new Vector2(.3f, .14f), Color.yellow);
            obj.AddComponent<BoxCollider2D>().isTrigger = true;
            Prototype.Body(obj, 0).linearVelocity = new Vector2(direction * 18, 0);
            obj.AddComponent<Projectile>();
            Destroy(obj, 1.5f);
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            if (spent) return;
            var enemy = other.GetComponent<Walker>();
            if (enemy == null && other.gameObject.layer != 8) return;
            spent = true;
            if (enemy != null) enemy.Hurt();
            Destroy(gameObject);
        }
    }
}
