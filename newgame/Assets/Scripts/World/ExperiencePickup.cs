using UnityEngine;

namespace NewGame
{
    public sealed class ExperiencePickup : MonoBehaviour
    {
        private bool collected;
        public static void Spawn(Vector2 position)
        {
            var obj = Prototype.Box("Experience", position, new Vector2(.35f, .35f), Color.green);
            obj.AddComponent<BoxCollider2D>();
            var trigger = obj.AddComponent<CircleCollider2D>();
            trigger.radius = 1.6f;
            trigger.isTrigger = true;
            Prototype.Body(obj).linearVelocity = new Vector2(Random.Range(-2f, 2f), 5);
            obj.AddComponent<ExperiencePickup>();
            Destroy(obj, 15);
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            var hero = other.GetComponent<PlayerController>();
            if (hero == null || collected) return;
            collected = true;
            hero.AddExperience(1);
            Destroy(gameObject);
        }
    }
}
