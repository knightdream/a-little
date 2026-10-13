using UnityEngine;

namespace NewGame
{
    public sealed class Walker : MonoBehaviour
    {
        private enum State { Patrol, Stunned, Charge }
        private State state;
        private Rigidbody2D body;
        private float direction = -1, stateUntil;
        private int health = 4;
        private bool dead;

        public static void Spawn(Vector2 position)
        {
            var obj = Prototype.Box("Walker", position, new Vector2(1.1f, .9f), new Color(1, .45f, .25f));
            obj.AddComponent<BoxCollider2D>();
            Prototype.Body(obj);
            obj.AddComponent<Walker>();
        }

        private void Awake() => body = GetComponent<Rigidbody2D>();

        private void FixedUpdate()
        {
            if (Physics2D.Raycast((Vector2)transform.position, new Vector2(direction, 0), .65f, 1 << 8))
                direction *= -1;
            if (state != State.Patrol && Time.time >= stateUntil) state = State.Patrol;
            float speed = state == State.Charge ? 6 : state == State.Stunned ? 0 : 1.5f;
            body.linearVelocity = new Vector2(direction * speed, body.linearVelocity.y);
            GetComponent<SpriteRenderer>().color = state == State.Charge ? Color.red : new Color(1, .45f, .25f);
        }

        public void Hurt()
        {
            if (dead) return;
            if (--health <= 0)
            {
                dead = true;
                ExperiencePickup.Spawn(transform.position);
                Destroy(gameObject);
                return;
            }
            // Original prototype rule: a second hit during stun triggers a charge.
            if (state == State.Stunned) { state = State.Charge; stateUntil = Time.time + 2; }
            else if (state == State.Patrol) { state = State.Stunned; stateUntil = Time.time + .8f; }
        }

        private void OnCollisionStay2D(Collision2D collision)
        {
            var hero = collision.gameObject.GetComponent<PlayerController>();
            if (hero != null) hero.Hurt(state == State.Charge ? 2 : 1);
        }
    }
}
