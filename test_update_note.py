import asyncio
import os
from dotenv import load_dotenv
from dinox_client import DinoxClient

# Load environment variables
load_dotenv()

async def test_update_note():
    api_token = os.getenv("DINOX_API_TOKEN")
    if not api_token:
        print("Error: DINOX_API_TOKEN not found in environment variables.")
        return

    async with DinoxClient(api_token=api_token) as client:
        # Use a dummy note ID or one provided by the user if available.
        # Since I don't have a guaranteed valid note ID, I'll use the one from the user's request example
        # hoping it might be valid or at least the server response will tell us if it's not found vs 404 on endpoint.
        # Ideally, I should create a note first, but `create_note` might also be complex.
        # Let's try to update the note ID from the user's curl command.
        note_id = "019a0984-ee0a-7c5a-a151-bb1666160037"
        
        print(f"Testing update_note for noteId: {note_id}")
        
        try:
            result = await client.update_note(
                note_id=note_id,
                content_md="# test updated by python client ... ",
                tags=["test2", "python-client"],
                title="test-2-2-python"
            )
            print("Update successful!")
            print(result)
        except Exception as e:
            print(f"Update failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_update_note())
