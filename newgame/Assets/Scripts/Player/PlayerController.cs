using UnityEngine;
using UnityEngine.SceneManagement;

namespace NewGame
{
    public sealed class PlayerController : MonoBehaviour
    {
        [SerializeField] private float speed = 7;
        [SerializeField] private float jumpSpeed = 12;
        public int Health { get; private set; } = 5;
        public int Experience { get; private set; }
        private Rigidbody2D body;
        private float move, facing = 1, jumpUntil, groundedUntil, nextShot, safeUntil;
        private readonly Collider2D[] groundHits = new Collider2D[4];
        private ContactFilter2D groundFilter;

        private void Awake()
        {
            body = GetComponent<Rigidbody2D>();
            groundFilter = new ContactFilter2D();
            groundFilter.SetLayerMask(1 << 8);
            groundFilter.useTriggers = false;
            jumpUntil = groundedUntil = -1;
        }

        private void Update()
        {
            move = (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow) ? 1 : 0)
                 - (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow) ? 1 : 0);
            if (move != 0) facing = Mathf.Sign(move);
            if (Input.GetKeyDown(KeyCode.Space)) jumpUntil = Time.time + .12f;
            if (Input.GetKey(KeyCode.J) && Time.time >= nextShot)
            {
                nextShot = Time.time + .18f;
                Projectile.Fire((Vector2)transform.position + new Vector2(facing * .6f, .1f), facing);
            }
            if (Input.GetKeyDown(KeyCode.R)) SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
            if (transform.position.y < -10) Respawn();
        }

        private void FixedUpdate()
        {
            var feet = (Vector2)transform.position + Vector2.down * .62f;
            bool grounded = Physics2D.OverlapBox(feet, new Vector2(.58f, .08f), 0, groundFilter, groundHits) > 0;
            if (grounded && body.linearVelocity.y <= .1f) groundedUntil = Time.time + .1f;
            var velocity = body.linearVelocity;
            velocity.x = move * speed;
            if (jumpUntil >= Time.time && groundedUntil >= Time.time)
            {
                velocity.y = jumpSpeed;
                jumpUntil = groundedUntil = -1;
            }
            velocity.y = Mathf.Max(velocity.y, -20);
            body.linearVelocity = velocity;
        }

        public void Hurt(int amount)
        {
            if (Time.time < safeUntil) return;
            safeUntil = Time.time + 1;
            Health -= amount;
            if (Health <= 0) Respawn();
        }

        public void AddExperience(int amount) => Experience += amount;

        private void Respawn()
        {
            Health = 5;
            transform.position = new Vector2(-8, 0);
            body.linearVelocity = Vector2.zero;
            safeUntil = Time.time + 1;
            jumpUntil = groundedUntil = -1;
        }
    }
}
